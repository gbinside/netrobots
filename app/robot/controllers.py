# Import flask dependencies
import time
from functools import wraps
from flask import Blueprint, Response, request, g, session
from app.robot.model import Robot
from hashlib import md5
import json
import app

# Define the blueprint: 'robot', set its url prefix: app.url/v1/robot
mod_robot = Blueprint('robot', __name__, url_prefix='/v1/robot')

def check_robot_token_and_limit_requests(original_function):
    @wraps(original_function)
    def new_function(token):
        if token in app.robot.hash_table:
            robot = app.robot.hash_table[token]
            assert isinstance(robot, Robot)

            # TODO I'm not sure that a lock is required here
            global_time = app.app.game_board.global_time()

            # TODO wait the needed time before answering to requests
            # TODO consider by default the next board time

            # TODO check if the time is passed, otherwise wait again

            # TODO si sincronizza su Event di thread, che segnala quando e` stata aggiornata la BOARD con un nuovo stat
            # - quando si risveglia il main thread aggiorna la board e avvisa che nel caso e` possibile inviare risposte e si mette in sleep
            # - il thread del server aggiorna i robot processando le richieste e usando il nuovo stato della TABLE

            # TODO siccome FIFO non e` garantita usa questo aproccio:
            # - manda un RETRY message
            # - il caller usa una procedura che semplicemente quando riceve il segnale rinvia il messaggio
            # - il server processa i messaggi in ordine, li presume quasi tutti FIFO
            # - quando riceve un messaggio da un CLIENT:
            # -- e` NEXT time date
            # -- mancano altri clients all'appello
            # -- segna nella BOARD che c'e` un OUT-OF-ORDER processing
            # -- manda segnale di ABORT al messaggio
            # -- processa gli altri messaggi in coda se ci sono
            # -- quando riceve di nuovo il messaggio dal PROCESS, si mette in WAIT del EVENT
            # -- quindi questo metodo fallisce se c'e` un processo che ha decisamente piu` priorita` degli altri nell'inviare le risposte:
            # --- invia la prima volta prima degli altri processi
            # --- riceve un abort
            # --- invia una risposta
            # --- la sua risposta e` processata nuovamente prima dei restanti messaggi
            # --- quindi viene usato anche come indicatore che tutti i messaggi al suo secondo passaggio, sono stati ricevuti e inviati

            if global_time > robot.last_command_executed_at_global_time:
               robot.last_command_executed_at_global_time = global_time
               return original_function(robot)
            else:
                # This client is sending too much requests, because it is not waiting for an answer.
                return Response(response=json.dumps({'status': 'KO', 'msg': 'Too many requests.'}),
                                status=500,
                                mimetype="application/json")
        else:
          return Response(response=json.dumps({'status': 'KO', 'msg': 'Invalid token.'}),
                          status=500,
                          mimetype="application/json")

    return new_function

# Set the route and accepted methods
@mod_robot.route('/<token>', methods=['DELETE'])
@check_robot_token_and_limit_requests
def delete_robot(robot):
    name = robot.get_name()
    if app.app.game_board.remove_robot(robot):
        app.robot.hash_table = dict([(x, y) for (x, y) in app.robot.hash_table.items() if y != robot])
        resp = Response(response=json.dumps({'status': 'OK', 'name': name}),
                        status=200,
                        mimetype="application/json")
        return resp

    resp = Response(response=json.dumps({'status': 'KO'}),
                    status=500,
                    mimetype="application/json")

    return resp


# Set the route and accepted methods
@mod_robot.route('/', methods=['POST'])
def new_robot():
    """
    create a new robot
    """
    if request.method == 'POST':
        name = request.form['name']
        extra = dict(
            max_hit_points=request.form.get('max_hit_points', None),
            max_speed=request.form.get('max_speed', None),
            acceleration=request.form.get('acceleration', None),
            decelleration=request.form.get('decelleration', None),
            max_sterling_speed=request.form.get('max_sterling_speed', None),
            max_scan_distance=request.form.get('max_scan_distance', None),
            max_fire_distance=request.form.get('max_fire_distance', None),
            bullet_speed=request.form.get('bullet_speed', None),
            bullet_damage=request.form.get('bullet_damage', None),
            reloading_time=request.form.get('reloading_time', None)
        )
        for k in extra:
            if extra[k] is not None:
                try:
                    extra[k] = int(extra[k])
                except ValueError:
                    extra[k] = json.loads(extra[k])

        if name:
            if name not in app.app.game_board.robots:
                _new_robot = Robot(app.app.game_board, name, count_of_other=len(app.app.game_board.robots),
                                   configuration=extra)
                if _new_robot.calc_value() > 327:
                    resp = Response(response=json.dumps({'status': 'KO',
                                                         'msg': "Robot too big: max points are 327; yours points: " +
                                                                str(_new_robot.calc_value())}),
                                    status=500,
                                    mimetype="application/json")
                    return resp

                app.app.game_board.robots[name] = _new_robot
                token = md5(name + time.strftime('%c')).hexdigest()
                app.robot.hash_table[token] = app.app.game_board.robots[name]

                resp = Response(response=json.dumps({'status': 'OK', 'token': token}),
                                status=200,
                                mimetype="application/json")
                return resp

            resp = Response(response=json.dumps({'status': 'KO', 'msg': "Robot with the same name already exists"}),
                            status=500,
                            mimetype="application/json")
            return resp

        resp = Response(response=json.dumps({'status': 'KO', 'msg': "Name can't be empty"}),
                        status=500,
                        mimetype="application/json")
        return resp

    resp = Response(response=json.dumps({'status': 'KO'}),
                    status=500,
                    mimetype="application/json")

    return resp

@mod_robot.route('/<token>/step', methods=['PUT'])
@check_robot_token_and_limit_requests
def step(robot):
    """This is the new API to use, containing all the commands in one step."""

    if request.form['scan_degree'] is not None:
        scan_degree = int(float(request.form['scan_degree']))
        scan_resolution = int(float(request.form['scan_resolution']))
    else:
        scan_degree = None
        scan_resolution = None

    if request.form['cannon_degree'] is not None:
        cannon_degree = request.form['cannon_degree']
        cannon_distance = request.form['cannon_distance']
    else:
        cannon_degree = None
        cannon_distance = None

    if request.form['drive_speed'] is not None:
        drive_speed = request.form['drive_speed']
        drive_degree = request.form['drive_degree']
    else:
        drive_speed = None
        drive_degree = None

    status = process_step(robot, scan_degree, scan_resolution, cannon_degree, cannon_distance, drive_speed, drive_degree)

    return Response(response=json.dumps({'robot_status': status}),
                    status=200,
                    mimetype="application/json")

def process_step(robot, scan_degree, scan_resolution, cannon_degree, cannon_distance, drive_speed, drive_degree):

    if scan_degree is not None:
        robot.scan(scan_degree, scan_resolution)
    else:
        robot.no_scan()

    if cannon_degree is not None:
        robot.cannon(cannon_degree, cannon_distance)
    else:
        robot.no_cannon()

    if drive_speed is not None:
        robot.drive(drive_degree, drive_speed)

    return robot.get_status()

@mod_robot.route('/<token>/data', methods=['GET'])
@check_robot_token_and_limit_requests
def robot_data(robot):
    resp = Response(response=json.dumps({'status': 'OK', 'robot': robot.get_data()}),
                    status=200,
                    mimetype="application/json")
    return resp

@mod_robot.route('/<token>', methods=['GET'])
@check_robot_token_and_limit_requests
def status(robot):
    """Legay API"""
    resp = Response(response=json.dumps({'status': 'OK', 'robot': robot.get_status()}),
                    status=200,
                    mimetype="application/json")
    return resp

@mod_robot.route('/<token>/drive', methods=['PUT'])
@check_robot_token_and_limit_requests
def drive(robot):
    """Legacy API."""

    speed = request.form['speed']
    degree = request.form['degree']
    ret = robot.drive(degree, speed)
    if ret:
        resp = Response(response=json.dumps({'status': 'OK', 'robot': robot.get_status(), 'done': ret}),
                        status=200,
                        mimetype="application/json")
        return resp

    resp = Response(response=json.dumps({'status': 'KO', 'robot': robot.get_status(), 'done': ret}),
                    status=406,
                    mimetype="application/json")
    return resp


@mod_robot.route('/<token>/scan', methods=['PUT'])
@check_robot_token_and_limit_requests
def scan(robot):
    """Legacy API."""

    degree = int(float(request.form['degree']))
    resolution = int(float(request.form['resolution']))
    assert isinstance(robot, Robot)
    ret = robot.scan(degree, resolution)

    if ret is not None:
        resp = Response(response=json.dumps({'status': 'OK', 'distance': ret}),
                        status=200,
                        mimetype="application/json")
        return resp

    resp = Response(response=json.dumps({'status': 'KO', 'distance': None}),
                    status=406,
                    mimetype="application/json")
    return resp


@mod_robot.route('/<token>/cannon', methods=['PUT'])
@check_robot_token_and_limit_requests
def cannon(robot):
    """Legacy API."""

    degree = request.form['degree']
    distance = request.form['distance']
    ret = robot.cannon(degree, distance)
    if ret:
        resp = Response(response=json.dumps({'status': 'OK', 'robot': robot.get_status(), 'done': ret}),
                        status=200,
                        mimetype="application/json")
        return resp

    resp = Response(response=json.dumps({'status': 'KO', 'robot': robot.get_status(), 'done': ret}),
                    status=406,
                    mimetype="application/json")
    return resp


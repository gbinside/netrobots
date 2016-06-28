import json
import time
from functools import wraps
from hashlib import md5

from flask import Blueprint, Response, request, g, session

import app
from app.robot.model import Robot

# Define the blueprint: 'robot', set its url prefix: app.url/v1/robot
mod_robot = Blueprint('robot', __name__, url_prefix='/v1/robot')


class TokenTable(object):
    def __init__(self, ttl):
        self._ttl = ttl
        self._last = {}

    def __call__(self, token):
        if token in self._last:
            wait_time = self._ttl - (time.time() - self._last[token])
            if wait_time > 0:
                return True
                # time.sleep(wait_time)
        self._last[token] = time.time()
        return False


# throttle decorator, number of call per second per token
def throttle(times_per_second_per_token):
    lock = TokenTable(ttl=1.0 / float(times_per_second_per_token))

    def decofunction(original_function):
        @wraps(original_function)
        def new_function(token):
            if lock(token):
                return Response(response=json.dumps({'status': 'KO'}),
                                status=509,
                                mimetype="application/json")
            return original_function(token)

        return new_function

    return decofunction


# login decorator
def check_token(original_function):
    @wraps(original_function)
    def new_function(token):
        if token in app.robot.hash_table:
            robot = app.robot.hash_table[token]
            assert isinstance(robot, Robot)
            return original_function(robot)

        resp = Response(response=json.dumps({'status': 'KO'}),
                        status=500,
                        mimetype="application/json")
        return resp

    return new_function


# Set the route and accepted methods
@mod_robot.route('/<token>', methods=['DELETE'])
@check_token
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


@mod_robot.route('/<token>', methods=['GET'])
@throttle(5)
@check_token
def status(robot):
    resp = Response(response=json.dumps({'status': 'OK', 'robot': robot.get_status()}),
                    status=200,
                    mimetype="application/json")
    return resp


@mod_robot.route('/<token>/data', methods=['GET'])
@throttle(5)
@check_token
def status_data(robot):
    resp = Response(response=json.dumps({'status': 'OK', 'robot': robot.get_data()}),
                    status=200,
                    mimetype="application/json")
    return resp


@mod_robot.route('/<token>/drive', methods=['PUT'])
@throttle(2)
@check_token
def drive(robot):
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
@throttle(2)
@check_token
def scan(robot):
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
@throttle(2)
@check_token
def cannon(robot):
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

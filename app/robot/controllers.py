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
@mod_robot.route('/', methods=['POST'])
def new_robot():
    """
    create a new robot
    """
    if request.method == 'POST':
        name = request.form['name']
        if name:
            if name not in app.app.game_board.robots:
                app.app.game_board.robots[name] = Robot(app.app.game_board, name, len(app.app.game_board.robots))
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
@check_token
def status(robot):
    resp = Response(response=json.dumps({'status': 'OK', 'robot': robot.get_status()}),
                    status=200,
                    mimetype="application/json")
    return resp


@mod_robot.route('/<token>/drive', methods=['PUT'])
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
@check_token
def scan(robot):
    degree = request.form['degree']
    resolution = request.form['resolution']
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

@mod_robot.route('/<token>/endturn', methods=['PUT'])
@check_token
def endturn(robot):
    ret = robot.endturn()
    if ret:
        resp = Response(response=json.dumps({'status': 'OK', 'robot': robot.get_status(), 'done': ret}),
                        status=200,
                        mimetype="application/json")
        return resp

    resp = Response(response=json.dumps({'status': 'KO', 'robot': robot.get_status(), 'done': ret}),
                    status=406,
                    mimetype="application/json")
    return resp
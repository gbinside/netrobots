# Import flask dependencies
import time
from flask import Blueprint, Response, request, g, session
from app.robot.model import Robot
from hashlib import md5
import json
import app

# Define the blueprint: 'robot', set its url prefix: app.url/v1/robot
mod_robot = Blueprint('robot', __name__, url_prefix='/v1/robot')


# Set the route and accepted methods
@mod_robot.route('/', methods=['POST'])
def new_robot():
    """
    create a new robot
    """
    if request.method == 'POST':
        name = request.form['name']
        if name:
            if name not in app.robot.robots:
                app.robot.robots[name] = Robot(name)
                token = md5(name+time.strftime('%c')).hexdigest()
                app.robot.hash_table[token] = app.robot.robots[name]
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
def status(token):
    if token in app.robot.hash_table:
        robot = app.robot.hash_table[token]
        resp = Response(response=json.dumps({'status': 'OK', 'robot': robot.get_status()}),
                        status=200,
                        mimetype="application/json")
        return resp

    resp = Response(response=json.dumps({'status': 'KO'}),
                    status=500,
                    mimetype="application/json")

    return resp
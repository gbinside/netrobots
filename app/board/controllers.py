# Import flask dependencies
from flask import Blueprint, Response, request, g, session
import json
import app

# Define the blueprint: 'board', set its url prefix: app.url/v1/board
mod_board = Blueprint('board', __name__, url_prefix='/v1/board')


# Set the route and accepted methods
@mod_board.route('/', methods=['GET'])
def get_board():
    """
    give back a json with the whole board
    """

    resp = Response(response=json.dumps(app.app.game_board.get_status()),
                    status=200,
                    mimetype="application/json")

    return resp

@mod_board.route('/reset', methods=['POST'])
def reset_board():
    app.app.game_board.reinit()
    app.robot.hash_table = {}
    resp = Response(response=json.dumps(app.app.game_board.get_status()),
                    status=200,
                    mimetype="application/json")

    return resp


# Import flask dependencies
from flask import Blueprint, Response, request, g, session
import app
import server.game_server as game_server
import zmq

# Define the blueprint: 'board', set its url prefix: app.url/v1/board
mod_board = Blueprint('board', __name__, url_prefix='/v1/board')

# Set the route and accepted methods
@mod_board.route('/', methods=['GET'])
def get_board():
    """
    give back a json with the whole board
    """

    socket = zmq.Context.instance().socket(zmq.REQ)
    socket.connect(app.app.local_queue_name)
    socket.send(game_server.COMMAND_GET_BOARD)
    board_status = socket.recv()
    socket.close()

    resp = Response(response=board_status,
                    status=200,
                    mimetype="application/json")

    return resp

@mod_board.route('/reset', methods=['POST'])
def reset_board():

    socket = zmq.Context.instance().socket(zmq.REQ)
    socket.connect(app.app.local_queue_name)
    socket.send(game_server.COMMAND_RESET_GAME)
    socket.recv()

    socket.send(game_server.COMMAND_GET_BOARD)
    board_status = socket.recv()

    socket.close()

    resp = Response(response=board_status,
                    status=200,
                    mimetype="application/json")

    return resp


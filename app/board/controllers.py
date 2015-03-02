# Import flask dependencies
from flask import Blueprint, Response, request, g
import app
import server.game_server as game_server
import zmq


def get_localSocket():
    """
    Open a socket only one time, and then cache it for each application context/thread.
    """
    socket = getattr(g, '_localSocket', None)
    if socket is None:
        socket = zmq.Context.instance().socket(zmq.REQ)
        socket.connect(app.app.local_queue_name)
        g._localSocket = socket
    return socket

@app.app.teardown_appcontext
def teardown_localSocket(exception):
    """
    This code is called when the resource must be discarded along with the application context/thread.
    """

    socket = getattr(g, '_localSocket', None)
    if socket is not None:
        socket.close()

# Define the blueprint: 'board', set its url prefix: app.url/v1/board
mod_board = Blueprint('board', __name__, url_prefix='/v1/board')

# Set the route and accepted methods
@mod_board.route('/', methods=['GET'])
def get_board():
    """
    give back a json with the whole board
    """

    socket = get_localSocket()

    socket.send(game_server.COMMAND_GET_BOARD)
    board_status = socket.recv()

    resp = Response(response=board_status,
                    status=200,
                    mimetype="application/json")

    return resp

@mod_board.route('/reset', methods=['POST'])
def reset_board():

    socket = get_localSocket()

    socket.send(game_server.COMMAND_RESET_GAME)
    socket.recv()

    socket.send(game_server.COMMAND_GET_BOARD)
    board_status = socket.recv()

    resp = Response(response=board_status,
                    status=200,
                    mimetype="application/json")

    return resp


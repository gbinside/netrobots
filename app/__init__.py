from flask import Flask, render_template, flash
import zmq
from server.game_server import WakeUpThread, GameThread

app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    flash('404 - page not found')
    return render_template('404.html', **app.config), 404

# Import a module / component using its blueprint handler variable (mod_board)
from app.board.controllers import mod_board as board_module
from app.viewer.controllers import mod_viewer as viewer_module

app.register_blueprint(board_module)
app.register_blueprint(viewer_module)

local_queue_name = "inproc://netrobots"
client_queue_name = "tcp://127.0.0.1:5555"

@app.before_first_request
def setup_game_server():
    thread1 = WakeUpThread(0.250, local_queue_name, client_queue_name)
    thread2 = GameThread(0.125, local_queue_name, client_queue_name)

    thread2.daemon = True
    thread2.start()

    thread1.daemon = True
    thread1.start()

    app.local_queue_name = local_queue_name


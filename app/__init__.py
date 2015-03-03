from flask import Flask, render_template, flash
from server.game_server import WakeUpThread, GameThread
from random import randint

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

# a unique internal ZMQ queue accepting internal commands
local_queue_name = "inproc://netrobots_" + str(randint(1, 100000))

#
# Manage Application Status Inside Web Server Contexts
#

@app.before_first_request
def setup_game_server():
    """This code is executed exactly one time, at application startup, and it starts GameServer threads."""

    # XXX
    log = open('debug.log', 'wb')
    log.write("\nStart of LOG FILE\n")

    thread1 = WakeUpThread(0.250, local_queue_name, app.config['SERVER_SOCKET'])
    thread2 = GameThread(0.125, local_queue_name, app.config['SERVER_SOCKET'], log)

    thread2.daemon = True
    thread2.start()

    thread1.daemon = True
    thread1.start()

    app.local_queue_name = local_queue_name

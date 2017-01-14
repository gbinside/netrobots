from flask import Flask, render_template, flash
from board.model import Board, BoardThread
from config import DELTATIME
from config import SLEEPTIME

# Define the WSGI application object
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
from app.robot.controllers import mod_robot as robot_module

app.register_blueprint(board_module)
app.register_blueprint(viewer_module)
app.register_blueprint(robot_module)

app.game_board = Board(float(DELTATIME/float(SLEEPTIME)))
app.game_board_th = BoardThread(app.game_board.tick, DELTATIME, SLEEPTIME)
app.game_board_th.daemon = True
app.game_board_th.start()

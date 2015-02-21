from flask import Blueprint, render_template
import app

mod_viewer = Blueprint('viewer', __name__)


@mod_viewer.route('/', methods=['GET'])
def home():
    return render_template('home.html', **app.app.config)

@mod_viewer.route('/nocanvas', methods=['GET'])
def home_nocanvas():
    return render_template('home_nocanvas.html', **app.app.config)
from flask import Blueprint, render_template
import app

mod_viewer = Blueprint('viewer', __name__)


@mod_viewer.route('/', methods=['GET'])
def home():
    return render_template('home.html', **app.app.config)
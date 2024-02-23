
from flask import Flask, request
from flask_debugtoolbar import DebugToolbarExtension
import sys, os
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb



app = Flask(__name__)


app.debug = True
app.config['SECRET_KEY'] = 'pyrosoma'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['DEBUG_TB_PROFILER_ENABLED'] = True
app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True

toolbar = DebugToolbarExtension(app)
Breadcrumbs(app=app)

basedir = os.path.abspath(os.path.dirname(__file__))

from app import views


 


from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
import os
#from flask_breadcrumbs import Breadcrumbs, register_breadcrumb
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager



BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(BASEDIR, "db.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)

app.debug = True
app.config['SECRET_KEY'] = 'pyrosoma'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['DEBUG_TB_PROFILER_ENABLED'] = True
app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True

#toolbar = DebugToolbarExtension(app)
#Breadcrumbs(app=app)


from app import views, routes
from dbmanager import is_db_created
is_db_created()

 

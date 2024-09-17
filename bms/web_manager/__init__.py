from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
import os
#from flask_breadcrumbs import Breadcrumbs, register_breadcrumb
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from requests.exceptions import ConnectionError

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'user.login'
oauth = OAuth()

def split_comma(value):
    v = value.split(',')
    if len(v) > 1:
        return v[0], v[1]
    else:
        return v[0], ''

def create_app():
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    app = Flask(__name__, static_folder="../../static")

    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(BASEDIR, "db.sqlite")
    app.config['SQLALCHEMY_BINDS'] = {
        'secondary': 'sqlite:///'+os.path.join("/app", "bms", "controller", "dbtemp.sqlite")
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

    app.debug = True
    app.config['SECRET_KEY'] = 'pyrosoma'
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
    app.config['DEBUG_TB_PROFILER_ENABLED'] = True
    app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    oauth.init_app(app)

    app.jinja_env.filters['split_comma'] = split_comma

    from bms.web_manager.routes import routes_blueprint
    app.register_blueprint(routes_blueprint)

    app.config['wwrsa'] = '' #ip
    app.config['wwrsb'] = '' #ip
    app.config['du'] = '0' #ip or 0 for default *.*.1.100
    app.config['TEMP_MONITORING_ALARM'] = False #if the temp > temp_alarm SET TRUE 
    app.config['TEMP_MONITORING_STATUS'] = False #temp monitoring status (not include if a temp alarm is set)
    app.config['TEMP_ALARM'] = 0 #temp limit alarm
    app.config['NO_CONN'] = {'status' : False}
    try:
        from bms.google.google_main import google_blueprint
        app.register_blueprint(google_blueprint)
    except ConnectionError as e:
        app.config['NO_CONN'] = {'status' : True,
                                 'response' : str(e)}
    except Exception as e:
        app.config['NO_CONN'] = {'status' : True,
                                 'response' : str(e)}


    from bms.controller.views import cmd_blueprint
    app.register_blueprint(cmd_blueprint)

    #toolbar = DebugToolbarExtension(app)
    #Breadcrumbs(app=app)

    return app

 

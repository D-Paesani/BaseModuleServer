from bms.web_manager.dbmanager import Users, gen_random_psw
from bms.web_manager import db
from bms.google.google_api import google
from flask import Flask, request, redirect, url_for, flash, Blueprint
from flask_login import login_user, current_user

google_blueprint = Blueprint('google', __name__, template_folder="../../templates")

@google_blueprint.route('/bms/google/login')
def google_login():
    # Effettua il login con Google
    return google.authorize_redirect(redirect_uri=url_for('google.google_authorize', _external=True))

@google_blueprint.route('/bms/google/authorize')
def google_authorize():
    # Gestisci il callback dell'autenticazione Google
    token = google.authorize_access_token()
    user_info = google.parse_id_token(token, None)
    
    # Controlla se l'utente esiste nel database
    user = Users.query.filter_by(email=user_info['email']).first()
    if not user:
        # Crea un nuovo utente nel database
        user = Users(email=user_info['email'], username=user_info['name'], password=gen_random_psw(), source='google')
        db.session.add(user)
        db.session.commit()
    else:
        up = Users.query.filter_by(id=user.id).first()
        up.password = gen_random_psw()
        db.session.add(up)
        db.session.commit()

    # Esegui il login dell'utente
    login_user(user)

    flash(f'WELCOME {current_user}', 'success-custom')
    return redirect(url_for('base'))
from forms import LoginForm
from dbmanager import Users, gen_random_psw
from app import app, bcrypt, db
from flask import Flask, request, render_template, redirect, url_for, flash
from forms import LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from google_api import google

@app.route('/bms/google/login')
def google_login():
    # Effettua il login con Google
    return google.authorize_redirect(redirect_uri=url_for('google_authorize', _external=True))

@app.route('/bms/google/authorize')
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





@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('base'))
    form = LoginForm()
    if request.method == "POST":
        ulogin = False
        if form.validate_on_submit():
            if Users.query.filter_by(username=form.username.data).first():
                ulogin = Users.query.filter_by(username=form.username.data).first()
            elif Users.query.filter_by(email=form.username.data).first():
                ulogin = Users.query.filter_by(email=form.username.data).first()
            if ulogin == False:
                flash('Username or Password not Found', 'danger-custom')
            elif ulogin and bcrypt.check_password_hash(ulogin.password, form.password.data):
                login_user(ulogin)
                flash(f'Login Successfully {current_user}', 'success-custom')
                return redirect(url_for('base'))
            else:
                flash("Wrong Password", 'danger-custom')
    return render_template('accounts/login.html', form=form)



@app.route('/logout')
@login_required
def logout():
    if current_user.source == 'google':
        Users.query.filter(Users.email == current_user.email).delete()
        db.session.commit()
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error)
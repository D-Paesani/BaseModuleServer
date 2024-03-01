from forms import LoginForm
from dbmanager import Users
from app import app, bcrypt
from flask import Flask, request, render_template, redirect, url_for, flash
from forms import LoginForm
from dbmanager import Users
from flask_login import login_user, current_user, logout_user, login_required







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
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error=error)
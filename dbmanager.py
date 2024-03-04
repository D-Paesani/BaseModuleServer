from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, login_manager
import os, random, string
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin

class Users(db.Model, UserMixin):

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    source = db.Column(db.String(16), nullable=False) #local, google
    is_active = db.Column(db.Boolean(), default=True)

    def __repr__(self):
        return f"{self.username}"

@login_manager.user_loader
def load_user(email):
    return Users.query.get(email)


def is_db_created():
    with app.app_context():
        db_file = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not os.path.isfile(db_file):
            db.create_all()
            db_admin = Users(username='guest', 
                             password=generate_password_hash('guess').decode('utf-8'), 
                             email='admin@email.com',
                             source='local')
            db.session.add(db_admin)
            db.session.commit()
            

def gen_random_psw():
    return generate_password_hash(''.join(random.choices(string.ascii_lowercase, k=32)))
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from bms.web_manager import db, login_manager
import os, random, string
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from .roles import Permission, Roles
#from ..controller.dbmanager import DeviceType

class Users(db.Model, UserMixin):

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    source = db.Column(db.String(16), nullable=False) #local, google
    is_active = db.Column(db.Boolean(), default=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __repr__(self):
        return f"{self.username}"
    
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)
    
    def get_role(self):
        return self.role.name if self.role else None
    
    def to_dict(self):
        return {'id': self.id,
                'username' : self.username,
                'password0' : self.password,
                'email' : self.email,
                'source' : self.source,
                'role_id' : self.role_id}
    

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

@login_manager.user_loader
def load_user(email):
    return Users.query.get(email)


def is_db_created():
    with current_app.app_context():
        db_file = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        print(db_file)
        if not os.path.isfile(db_file):
            db.create_all(bind_key=None)
            db_admin = Users(username='guest', 
                             password=generate_password_hash('guess').decode('utf-8'), 
                             email='admin@email.com',
                             source='local',
                             role_id=1)
            db.session.add(db_admin)
            db.session.commit()

            db_roles = Roles(id=3, name='reader', default=True, permissions=1)
            db.session.add(db_roles)
            db.session.commit()

            db_roles = Roles(id=2, name='edit', default=True, permissions=3)
            db.session.add(db_roles)
            db.session.commit()

            db_roles = Roles(id=1, name='admin', default=True, permissions=7)
            db.session.add(db_roles)
            db.session.commit()
        
        for bind_key, bind_uri in current_app.config['SQLALCHEMY_BINDS'].items():
            db_file = bind_uri.replace('sqlite:///', '')
            print(db_file)
            if not os.path.isfile(db_file):
                db.create_all(bind_key="secondary")
                
                # weta = DeviceType(type="wwrs_a")
                # db.session.add(weta)
                # db.session.commit()

                # wetb = DeviceType(type="wwrs_b")
                # db.session.add(wetb)
                # db.session.commit()

                # clb_fpga = DeviceType(type="clb_fpga")
                # db.session.add(clb_fpga)
                # db.session.commit()
            

def gen_random_psw():
    return generate_password_hash(''.join(random.choices(string.ascii_lowercase, k=32)))
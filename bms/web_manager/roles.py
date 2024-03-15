from . import db



class Permission:
    READ = 1
    EDIT = 2
    ADMIN = 4

class Roles(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(6), unique=True)
    default = db.Column(db.Boolean, nullable=False)
    permissions = db.Column(db.Integer, nullable=False)

    users = db.relationship('Users', backref='role', lazy='dynamic')


    def has_permission(self, perm):
        return self.permissions & perm == perm
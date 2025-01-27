from bms.web_manager import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError

# class Dudev(db.Model):
#     __bind_key__ = 'secondary'
#     __tablename__ = 'device'
    
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     ip = db.Column(db.String(15), nullable=False)
#     du = db.Column(db.Integer, nullable=False)
#     iddevicetype = db.Column(db.Integer, db.ForeignKey('devicetype.id'))

# class DeviceType(db.Model):
#     __bind_key__ = 'secondary'
#     __tablename__ = 'devicetype'
    
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     type = db.Column(db.String(4), unique=True, nullable=False)

#     temperatures = db.relationship("Temperature", backref="devicetype", lazy=True)
#     dudevs = db.relationship("Dudev", backref="devicetype", lazy=True)

class Temperature(db.Model):
    __bind_key__ = 'secondary'
    __tablename__ = 'temperature'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    temperature = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    du = db.Column(db.Integer, nullable=False)
    clb_ip = db.Column(db.String(15))
    wwrsa_ip = db.Column(db.String(15))
    wwrsb_ip = db.Column(db.String(15))
    temp1 = db.Column(db.Boolean)
    temp2 = db.Column(db.Boolean)
    dul = db.Column(db.Boolean)

    def __repr__(self):
        return(f"{self.id}")


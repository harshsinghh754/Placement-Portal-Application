from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  
    is_active = db.Column(db.Boolean, default=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    resume = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    user = db.relationship("User")


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_name = db.Column(db.String(150))
    approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)


class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    deadline = db.Column(db.Date)
    approved = db.Column(db.Boolean, default=False)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'))
    status = db.Column(db.String(20), default="Applied")
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
from app import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # password should be stored as a hash
    name = db.Column(db.String(100))  # The name column
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    number = db.Column(db.String(15))
    user_type = db.Column(db.String(20), nullable=False, default='customer') 
    behaviors = db.relationship("UserBehavior", back_populates="user")
    

    behaviors = db.relationship('UserBehavior', backref='related_user', lazy='dynamic')  # Renamed backref to avoid conflicts

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

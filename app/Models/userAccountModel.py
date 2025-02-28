from ..extensions import db
from sqlalchemy.orm import relationship
from datetime import datetime

class UserAccount(db.Model):
    __tablename__ = 'user_account_table'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_username = db.Column(db.String(255), nullable=False, unique=True)
    user_password = db.Column(db.String(255), nullable=False)
    user_name = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(255), nullable=False, unique=True)
    user_phone = db.Column(db.String(255), nullable=False)
    user_address = db.Column(db.String(255), nullable=False)
    user_location = db.Column(db.String(255), nullable=False)
    user_weather = db.Column(db.String(255), nullable=False)
    user_profile_picture = db.Column(db.String(255), nullable=True)
    user_time_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_username, user_password, user_name, user_email, user_phone, 
                 user_address, user_location, user_weather, user_profile_picture):
        self.user_username = user_username
        self.user_password = user_password
        self.user_name = user_name
        self.user_email = user_email
        self.user_phone = user_phone
        self.user_address = user_address
        self.user_location = user_location
        self.user_weather = user_weather
        self.user_profile_picture = user_profile_picture

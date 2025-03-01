from datetime import UTC, datetime

from sqlalchemy.orm import relationship

from ..extensions import db


class UserAccount(db.Model):
    __tablename__ = 'user_account'

    user_id = db.Column(db.Integer, primary_key=True)
    user_username = db.Column(db.String(50), unique=True, nullable=False)
    user_password = db.Column(db.String(255), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(120), unique=True, nullable=False)
    user_phone = db.Column(db.String(20))
    user_address = db.Column(db.String(200))
    user_location = db.Column(db.String(100))
    user_weather = db.Column(db.String(100))
    user_profile_picture = db.Column(db.String(255))
    user_time_created = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    def __init__(self, user_username, user_password, user_name, user_email, user_phone=None, 
                 user_address=None, user_location=None, user_weather=None, user_profile_picture=None):
        self.user_username = user_username
        self.user_password = user_password
        self.user_name = user_name
        self.user_email = user_email
        self.user_phone = user_phone or ''
        self.user_address = user_address or ''
        self.user_location = user_location or ''
        self.user_weather = user_weather or ''
        self.user_profile_picture = user_profile_picture or ''

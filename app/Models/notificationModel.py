from ..extensions import db
from sqlalchemy.orm import relationship
from datetime import datetime


class Notification(db.Model):
    __tablename__ = 'notification_table'

    notification_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_account_table.user_id'))
    user_severe_weather_alert = db.Column(db.Integer, db.ForeignKey('user_account_table.user_severe_weather_account'))
    notification_message = db.Column(db.String(255), nullable=False)
    delivery_status = db.Column(db.String(255), nullable=False)
    time_created = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def __init__(self, notification_id, user_id, notification_message, delivery_status):

            self.notification_id = notification_id,
            self.user_id = user_id,   
            self.notification_message = notification_message,
            self.delivery_status = delivery_status
from ..extensions import db
from sqlalchemy.orm import relationship
from datetime import datetime


class Friendship(db.Model):
    __tablename__ = 'friendship_table'

    user1_id = db.Column(db.Integer, db.ForeignKey('user_account_table.user_id'), primary_key=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('user_account_table.user_id'), primary_key=True)
    friendship_status = db.Column(db.String(255), nullable=False)
    time_created = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def __init__(self, user1_id, user2_id, friendship_status):
    
            self.user1_id = user1_id,
            self.user2_id = user2_id,  
            self.friendship_status = friendship_status

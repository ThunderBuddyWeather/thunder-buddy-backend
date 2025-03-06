from ..extensions import db
from sqlalchemy.orm import relationship
from datetime import datetime


class Group(db.Model):
    __tablename__ = 'group_table'

    group_id = db.Column(db.String(255), nullable=False)
    group_name = db.Column(db.String(255), nullable=False)
    group_members = db.Column(db.String(255), nullable=False)
    time_created = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def __init__(self, group_id, group_name, group_members ):
    
            self.group_id = group_id,
            self.group_name = group_name,  
            self.group_members = group_members

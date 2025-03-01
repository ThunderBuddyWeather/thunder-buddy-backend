from datetime import UTC, datetime

from sqlalchemy.orm import relationship

from app.extensions import db


class Friendship(db.Model):
    __tablename__ = "friendship_table"

    user1_id = db.Column(
        db.Integer, db.ForeignKey("user_account.user_id"), primary_key=True
    )
    user2_id = db.Column(
        db.Integer, db.ForeignKey("user_account.user_id"), primary_key=True
    )
    friendship_status = db.Column(db.String(50), nullable=False)
    time_created = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )

    def __init__(self, user1_id, user2_id, friendship_status):
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.friendship_status = friendship_status

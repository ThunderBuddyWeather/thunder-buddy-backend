from sqlalchemy import Column, Integer, String
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db  # Ensure this imports your SQLAlchemy instance

class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # Renamed from password_hash

    def set_password(self, password):
        """Hash and store the user's password."""
        self.password = generate_password_hash(password)  # Updates password column

    def check_password(self, password):
        """Verify a password against the stored hash."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"
    
# Database Model for a table (for example, WeatherLogs)
class WeatherLog(db.Model):
    __tablename__ = 'weather_logs'

    id = db.Column(db.Integer, primary_key=True)
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(2))
    temperature = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<WeatherLog {self.zip_code}, {self.country}, {self.temperature}, {self.timestamp}>"

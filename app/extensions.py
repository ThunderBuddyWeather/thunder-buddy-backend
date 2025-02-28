from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache


limiter = Limiter(
    key_func= get_remote_address,
    default_limits=["100 per hour"]  
)
db = SQLAlchemy()
ma = Marshmallow()
caching = Cache() 

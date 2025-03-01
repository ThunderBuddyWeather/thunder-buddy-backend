from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

migrate = Migrate()
jwt = JWTManager()

# Update caching to use direct backend class
caching = Cache(config={
    'CACHE_TYPE': 'flask_caching.backends.SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Update limiter to use Redis for production
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",  # This will be overridden in production config
    storage_options={},
    default_limits=["200 per day", "50 per hour"]
)

db = SQLAlchemy()
ma = Marshmallow() 

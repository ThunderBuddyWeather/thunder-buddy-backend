from flask import Flask  
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_caching import Cache 
from flask_cors import CORS
from dotenv import load_dotenv
from .Models import userAccountModel  
from .config import DevelopmentConfig, TestingConfig, ProductionConfig
from .extensions import limiter, ma, caching, db


from .Routes.userAccountRoute import user_account_blueprint
from .Routes.friendshipRoute import friendship_blueprint

migrate = Migrate() 
jwt = JWTManager()


def create_app(config_name):
    app = Flask(__name__)
    load_dotenv()  

    if config_name == 'testing':
        app.config.from_object(TestingConfig)
    elif config_name == 'development':
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(ProductionConfig)

  # Debugging line

    db.init_app(app)  # ✅ Make sure db.init_app() only runs if URI exists
    migrate.init_app(app, db) 
    ma.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)
    CORS(app)
        
    
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    caching.init_app(app)

    
    app.register_blueprint(user_account_blueprint, url_prefix='/user_account')
    app.register_blueprint(friendship_blueprint, url_prefix='/friendship')

    with app.app_context():
        db.create_all()
    
    return app  




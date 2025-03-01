from dotenv import load_dotenv
from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint

from .config import DevelopmentConfig, ProductionConfig, TestingConfig
from .extensions import caching, db, limiter, ma
from .Models import userAccountModel
from .Routes.friendshipRoute import friendship_blueprint
from .Routes.userAccountRoute import user_account_blueprint

migrate = Migrate()
jwt = JWTManager()


def create_app(config_name):
    app = Flask(__name__, static_url_path="/static", static_folder="../static")
    load_dotenv()

    if config_name == "testing":
        app.config.from_object(TestingConfig)
    elif config_name == "development":
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

    app.config["CACHE_TYPE"] = "simple"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300
    caching.init_app(app)

    # Configure Swagger UI
    SWAGGER_URL = "/apidocs"  # URL for exposing Swagger UI
    API_URL = "/static/swagger.yaml"  # Our API url (can be a local file)

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            "app_name": "Thunder Buddy API",
            "layout": "BaseLayout",
            "deepLinking": True,
            "showExtensions": True,
            "showCommonExtensions": True,
        },
    )

    # Register Swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    app.register_blueprint(user_account_blueprint, url_prefix="/api/user")
    app.register_blueprint(friendship_blueprint, url_prefix="/api/friends")

    with app.app_context():
        db.create_all()

    return app

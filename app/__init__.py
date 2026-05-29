import os
from flask import Flask
from dotenv import load_dotenv
from .extensions.db import mongo
from .extensions.limiter import limiter
from app.extensions.swagger import swagger
from app.modules.auth.routes import auth_bp
from app.modules.csv.routes import csv_bp
from app.modules.test.routes import test_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # JWT Configuration
    app.config["SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ALGORITHM"] = os.getenv("JWT_ALGORITHM", "HS256")
    app.config["JWT_EXPIRATION_HOURS"] = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # MongoDB Configuration
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/mydb")
    
    # Initialize extensions
    mongo.init_app(app)
    limiter.init_app(app)
    swagger.init_app(app)
    
    # Register blueprints
    app.register_blueprint(test_bp, url_prefix="/api/test")
    app.register_blueprint(csv_bp, url_prefix="/api/csv")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    
    return app
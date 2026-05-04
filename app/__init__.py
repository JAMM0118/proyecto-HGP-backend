from flask import Flask
from .extensions.db import mongo
from app.extensions.swagger import swagger
from app.modules.csv.routes import csv_bp
from app.modules.test.routes import test_bp

def create_app():
    app = Flask(__name__)
    
    app.config["MONGO_URI"] = "mongodb://localhost:27017/mydb"
    
    mongo.init_app(app)
    swagger.init_app(app)
    app.register_blueprint(test_bp, url_prefix="/api/test")
    app.register_blueprint(csv_bp, url_prefix="/api/csv")
    
    return app
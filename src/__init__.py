from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()

def init_admin(app):
    with app.app_context():
        from .models import Admin
        # Check if admin already exists
        admin = Admin.query.filter_by(username="mariocarballo").first()
        if not admin:
            admin = Admin(username="mariocarballo")
            admin.set_password("@jHt1vl09!")  # Default password, change in production
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")
        else:
            print("Admin user already exists")

def create_app():
    app = Flask(__name__)
    
    # Ensure the instance folder exists
    os.makedirs(os.path.dirname(os.path.abspath('instance/app.db')), exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    CORS(app)

    from .routes import api
    app.register_blueprint(api)

    # Initialize database and admin user
    with app.app_context():
        db.create_all()
        init_admin(app)

    return app

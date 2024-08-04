from flask import Flask, render_template
from config import Config
from extensions import db
from flask_migrate import Migrate
from routes import main
from models.models import Admin

def create_app():
    app = Flask(__name__)
    app.secret_key = "secret_key"
    app.config.from_object(Config)
    register_resource(app)
    register_extensions(app)
    create_default_admin(app)
    return app

def register_extensions(app):
    db.init_app(app)
    Migrate(app, db)

def create_default_admin(app):
    with app.app_context():
        admin = Admin.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = Admin(email='admin@example.com', password='123')
            db.session.add(admin)
            db.session.commit()

def register_resource(app):
    app.register_blueprint(main)

if __name__ == "__main__":
    app = create_app()
    app.app_context().push()
    app.run('127.0.0.1', 5000)
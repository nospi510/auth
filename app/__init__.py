from flask import Flask
from flask_login import LoginManager
from app.config import Config
from app.models import User  # Assure-toi d'importer ton modèle User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  

    # User Loader pour Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_user_by_id(user_id)  # Utilise une méthode pour récupérer l'utilisateur

    from app.routes import auth_bp
    app.register_blueprint(auth_bp)

    return app

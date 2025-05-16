from flask import Flask, g
from .extensions import Session, login_manager
from datetime import timedelta


def create_app():
    app = Flask(__name__)
    app.secret_key = 'your-secret-key'

    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Safe session handling per request
    @app.before_request
    def create_session():
        g.db = Session()

    @app.teardown_request
    def shutdown_session(exception=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()


    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

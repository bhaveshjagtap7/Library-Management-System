from flask import Flask
from app.routes.api import api_blueprint


def create_app(testing=False):
    """Application factory."""
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='../static'
    )

    app.config['TESTING'] = testing
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = 'enterprise-library-secret-key-2024'

    # Register blueprints
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Register frontend routes
    from app.routes.frontend import frontend_blueprint
    app.register_blueprint(frontend_blueprint)

    return app

import os
from sanic import Sanic


def _register_blueprints(app):
    from routes import bp
    app.blueprint(bp)


def _init_app(app, config):
    app.ctx.config = config
    app.ctx.clients = []
    _register_blueprints(app)


def create_app(config, **kwargs):
    """Creates and initializes the sanic application"""
    app = Sanic(os.environ.get('SANIC_APP_NAME'), **kwargs)
    _init_app(app, config)
    return app


def run_app(app, host='localhost', port=8000, workers=1, **kwargs):
    """Runs the application"""
    app.run(host=host, port=port, workers=workers, **kwargs)


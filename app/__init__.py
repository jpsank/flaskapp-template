import logging
from logging.handlers import RotatingFileHandler
import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_uploads import UploadSet, IMAGES, configure_uploads

import config


# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
# Flask-Login
login = LoginManager()
login.login_view = 'auth.login'
# Flask-Uploads
images = UploadSet('images', IMAGES)
# Flask-Session
sess = Session()


def create_app():
    # Create application
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    app.config.from_pyfile('config.py')

    # Initialize Sentry if possible
    if app.config['SENTRY_DSN']:
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration(), SqlalchemyIntegration()]
        )

    # Bind Flask extensions to application object
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    # Flask-Login
    login.init_app(app)
    # Flask-Uploads
    configure_uploads(app, images)
    # Flask-Session
    app.config['SESSION_SQLALCHEMY'] = db
    sess.init_app(app)

    # Blueprints
    from app import blueprints
    blueprints.init_app(app)

    # Set logging
    if not app.debug and not app.testing:
        if not os.path.exists(app.config['LOGS_PATH']):
            os.mkdir(app.config['LOGS_PATH'])
        file_handler = RotatingFileHandler(os.path.join(app.config['LOGS_PATH'], 'website.log'),
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('WEBSITE startup')

    with app.app_context():
        from app.util import filters

    return app


from app import models

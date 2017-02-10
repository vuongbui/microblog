import os
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_openid import OpenID
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from whoosh.filedb.filestore import FileStorage
from whoosh.fields import Schema, TEXT, ID
from config import WHOOSH_BASE
from .momentjs import momentjs



app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
mail = Mail(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
oid = OpenID(app, os.path.join(basedir, 'tmp'))
app.jinja_env.globals['momentjs'] = momentjs

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('microblog startup')


search_is_new = False
if not os.path.exists(WHOOSH_BASE):
    os.mkdir(WHOOSH_BASE)
    search_is_new = True
search_storage = FileStorage(WHOOSH_BASE)
search_ix = None
if search_is_new:
    schema = Schema(id=ID(stored=True), body = TEXT())
    search_ix = search_storage.create_index(schema)
else:
    search_ix = search_storage.open_index()

from app import views, models


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.secret_key = 'secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.config['MANAGE_CATEGORY_PERMISSION_LEVEL'] = 100
app.config['MANAGE_SUB_CATEGORY_PERMISSION_LEVEL'] = 100

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


from forumapp import routes
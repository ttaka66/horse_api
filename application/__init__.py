from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('application.config')

db = SQLAlchemy(app)

from application.views import admin
app.register_blueprint(admin.bp)

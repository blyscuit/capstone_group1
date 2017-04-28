from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:0904@localhost/kaidee'
db = SQLAlchemy(app)

class verifications(db.Model):
    _tablename_='verifications'
    id=db.Column('user_id',db.Integer,primary_key=True)
    verification_level=db.Column('verification_level', db.Unicode)
    
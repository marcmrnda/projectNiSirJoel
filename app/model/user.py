from .. import db
from sqlalchemy.sql import func

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    middleName = db.Column(db.String(100), nullable=True)
    lastName = db.Column(db.String(100), nullable=False)
    dateOfBirth = db.Column(db.Date, nullable=False)
    emailAddress = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(10), default="User")
    createdOn = db.Column(db.DateTime(timezone=True), default=func.now())
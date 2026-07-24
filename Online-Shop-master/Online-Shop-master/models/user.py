from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from extentions import db, get_current_time
from flask_login import UserMixin
from sqlalchemy.orm import relationship

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    phone = Column(String(11), nullable=False)
    address = Column(String, nullable=False)


from sqlalchemy import *
from extentions import db


class StockHistory(db.Model):
    __tablename__ = "stock_history"

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("products.id"))

    count = Column(Integer, nullable=False)

    submit_time = Column(String, nullable=False)

    action = Column(String, nullable=False)   # اضافه شود

    product = db.relationship("Product")
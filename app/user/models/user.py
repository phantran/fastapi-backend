from sqlalchemy import BigInteger, Column, Enum, Float, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship

from app.product.models.product import Product  # noqa
from core.db import Base
from core.db.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(Unicode(255), nullable=False, unique=True)
    password = Column(Unicode(255), nullable=False)
    deposit = Column(Float, nullable=False, default=0)
    role = Column(Unicode(255), nullable=False)
    products = relationship("Product")

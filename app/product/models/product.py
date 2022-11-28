from sqlalchemy import Column, Unicode, BigInteger, ForeignKey, Integer

from core.db import Base
from core.db.mixins import TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_name = Column(Unicode(255), nullable=False)
    seller_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
    )
    amount_available = Column(Integer, nullable=False)
    cost = Column(BigInteger, nullable=False)

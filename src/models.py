from __future__ import annotations

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

if __package__:
    from .database import Base
else:
    from database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    contact = Column(String(120), nullable=False)
    support_type = Column(String(80), nullable=False)
    notes = Column(Text, default="")

    food_items = relationship("FoodItem", back_populates="supplier")
    donations = relationship("DonatedSupply", back_populates="supplier")


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, unique=True)
    category = Column(String(80), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    sale_price = Column(Float, nullable=False, default=0.0)
    description = Column(Text, default="")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)

    supplier = relationship("Supplier", back_populates="food_items")


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    group_type = Column(String(60), nullable=False)
    role = Column(String(80), nullable=False)
    availability = Column(String(80), default="Disponível")
    notes = Column(Text, default="")


class DonatedSupply(Base):
    __tablename__ = "donated_supplies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    unit = Column(String(40), nullable=False, default="unidade")
    description = Column(Text, default="")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)

    supplier = relationship("Supplier", back_populates="donations")

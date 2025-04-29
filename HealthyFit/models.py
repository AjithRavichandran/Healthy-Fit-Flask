from .extensions import Base
from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from typing import List

class User(Base, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    phone: Mapped[str] = mapped_column(String(10), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    age: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    current_weight: Mapped[float] = mapped_column(Float, nullable=False)
    target_weight: Mapped[float] = mapped_column(Float, nullable=True)
    bmi: Mapped[float] = mapped_column(Float, nullable=True)
    activity_level: Mapped[float] = mapped_column(Float, nullable=True)
    pace: Mapped[float] = mapped_column(Float, nullable=True)
    adjusted_calories: Mapped[float] = mapped_column(Float, nullable=True)

    food_recommendations: Mapped[List["FoodRecommendation"]] = relationship("FoodRecommendation", back_populates="user")


class FoodRecommendation(Base):
    __tablename__ = 'food_recommendation'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recommended_food: Mapped[str] = mapped_column(String(255), nullable=False)
    count: Mapped[float] = mapped_column(Float, nullable=True)
    gram: Mapped[float] = mapped_column(Float, nullable=True)
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    sesion: Mapped[str] = mapped_column(String(255))
    ses: Mapped[str] = mapped_column(String(255))

    user: Mapped["User"] = relationship("User", back_populates="food_recommendations")

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel
from pydantic import Field as PydanticField
from sqlmodel import Field, Relationship, SQLModel


class MealItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    meal_id: Optional[int] = Field(default=None, foreign_key="meal.id", index=True)
    food_item_id: Optional[int] = Field(
        default=None, foreign_key="fooditem.id", index=True
    )
    quantity: float = Field(default=1.0)
    unit: Optional[str] = Field(default="serving")
    calories: Optional[float] = None
    meal: Optional["Meal"] = Relationship(back_populates="items")


class MealBase(SQLModel):
    name: Optional[str] = Field(default="meal")
    eaten_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None


class Meal(MealBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    total_calories: Optional[float] = Field(default=0.0)
    items: List[MealItem] = Relationship(back_populates="meal")
    image_url: Optional[str] = None


class MealFormCreate(BaseModel):
    name: Optional[str] = PydanticField(default="meal")
    notes: Optional[str] = None
    items: List[int] = PydanticField(default=[])
    total_calories: Optional[float] = PydanticField(default=0.0)

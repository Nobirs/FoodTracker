from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, SQLModel


class FoodItemBase(SQLModel):
    name: str
    brand: Optional[str] = None
    serving_size: Optional[float] = None
    serving_unit: Optional[str] = "g"
    calories_per_serving: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    nutrients: Optional[Dict[str, Any]] = Field(
        sa_column=Column(JSONB), default_factory=dict
    )
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))


class FoodItem(FoodItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_by: Optional[int] = Field(default=None, foreign_key="user.id", index=True)


class FoodCreate(FoodItemBase):
    pass


class FoodRead(FoodItemBase):
    id: int

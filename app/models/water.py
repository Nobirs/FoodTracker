from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class WaterIntakeBase(SQLModel):
    amount_ml: int = Field(..., gt=0)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WaterIntake(WaterIntakeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)


class WaterCreate(WaterIntakeBase):
    pass


class WaterRead(WaterIntakeBase):
    id: int
    user_id: int

from sqlmodel import SQLModel

from app.models import activity  # noqa: F401
from app.models import audit  # noqa: F401
from app.models import food  # noqa: F401
from app.models import meal  # noqa: F401
from app.models import template  # noqa: F401
from app.models import user  # noqa: F401
from app.models import water  # noqa: F401

metadata = SQLModel.metadata

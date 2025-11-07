# app/database/base.py
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

class Base(AsyncAttrs, DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Provides async ORM support for declarative models.
    """
    pass

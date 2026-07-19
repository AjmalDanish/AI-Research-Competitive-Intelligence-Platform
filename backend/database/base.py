"""
Database Base Module

SQLAlchemy declarative base and common database utilities.

Purpose:
- Define SQLAlchemy declarative base
- Provide common database models base class
- Include common model fields and methods

Clean Architecture:
- Infrastructure layer
- No business logic
- Pure database modeling
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base.

    All database models should inherit from this class.
    It provides common fields and methods for all models.
    """

    pass


class TimestampMixin:
    """
    Mixin for timestamp fields.

    Provides created_at and updated_at timestamps
    for models that need audit information.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality.

    Provides deleted_at field for soft deletes.
    Models with this mixin can be marked as deleted
    without actually removing them from the database.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    @property
    def is_deleted(self) -> bool:
        """Check if record is marked as deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark record as deleted."""
        from datetime import timezone

        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """Restore soft-deleted record."""
        self.deleted_at = None


# Export for easy import
__all__ = [
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
]

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    values = relationship(
        "MachineFieldValue",
        back_populates="machine",
        cascade="all, delete-orphan",
    )


class MachineField(Base):
    __tablename__ = "machine_fields"

    id = Column(Integer, primary_key=True, index=True)

    key = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    field_type = Column(
        String(20),
        nullable=False,
    )

    required = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    options = Column(
        Text,
        nullable=True,
    )

    values = relationship(
        "MachineFieldValue",
        back_populates="field",
        cascade="all, delete-orphan",
    )


class MachineFieldValue(Base):
    __tablename__ = "machine_field_values"

    id = Column(Integer, primary_key=True, index=True)

    machine_id = Column(
        Integer,
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
    )

    field_id = Column(
        Integer,
        ForeignKey("machine_fields.id", ondelete="CASCADE"),
        nullable=False,
    )

    value = Column(
        Text,
        nullable=False,
    )

    machine = relationship(
        "Machine",
        back_populates="values",
    )

    field = relationship(
        "MachineField",
        back_populates="values",
    )

    __table_args__ = (
        UniqueConstraint(
            "machine_id",
            "field_id",
            name="uq_machine_field_value",
        ),
    )
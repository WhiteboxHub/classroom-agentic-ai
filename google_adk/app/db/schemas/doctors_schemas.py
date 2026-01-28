from datetime import datetime, date, time
from uuid import UUID
from enum import Enum

from sqlalchemy import (
    Column, String, Boolean, Date, Time,
    ForeignKey, CheckConstraint, TIMESTAMP
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()




class AppointmentStatus(str, Enum):
    booked = "booked"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    rescheduled = "rescheduled"


class DoctorORM(Base):
    __tablename__ = "doctors"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    specialization = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP)

    appointments = relationship("AppointmentORM", back_populates="doctor")


class PatientORM(Base):
    __tablename__ = "patients"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(50))
    created_at = Column(TIMESTAMP)


class AppointmentORM(Base):
    __tablename__ = "appointments"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)

    doctor_id = Column(PG_UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(PG_UUID(as_uuid=True), ForeignKey("patients.id"))

    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    status = Column(String(30), nullable=False)

    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    doctor = relationship("DoctorORM", back_populates="appointments")
    patient = relationship("PatientORM")

    __table_args__ = (
        CheckConstraint(
            "status IN ('booked','confirmed','cancelled','completed','rescheduled')"
        ),
    )


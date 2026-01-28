
from datetime import date as DateType, time as TimeType
from db.schemas.doctors_schemas import DoctorORM, AppointmentORM, AppointmentStatus
from datetime import date, time
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from typing import Optional
from db.session import get_db
from core.logging import get_logger

logger = get_logger(__name__, log_file="logs/app.log")
def appointment_list(doctor_name: str) -> str:

    class AppointmentListSchema(BaseModel):
            appointment_date: date
            appointment_time: time
            status: AppointmentStatus
            patient_name: Optional[str]

            class Config:
                from_attributes = True  # ← IMPORTANT

    try:
    

    
        session = get_db()

        doctor = (
            session.query(DoctorORM)
            .filter(DoctorORM.name.ilike(f"%{doctor_name}%"))
            .first()
        )

        if not doctor:
            return f"No doctor found with name {doctor_name}"

        appointments = (
            session.query(AppointmentORM)
            .filter(AppointmentORM.doctor_id == doctor.id)
            .order_by(
                AppointmentORM.appointment_date,
                AppointmentORM.appointment_time
            )
            .all()
        )

        if not appointments:
            return f"No appointments found for {doctor_name}"

        # ORM → Pydantic
        result = [
            AppointmentListSchema(
                appointment_date=a.appointment_date,
                appointment_time=a.appointment_time,
                status=a.status,
                patient_name=a.patient.name if a.patient else None
            )
            for a in appointments
        ]

        lines = []
        for r in result:
            patient = r.patient_name or "Walk-in"
            lines.append(
                f"{r.appointment_date} {r.appointment_time} | "
                f"{r.status.value} | Patient: {patient}"
            )
        print(f" the orm result is {result}")
        session.close()
    except Exception as e:
        print(f"error in appointment list {e}")
    return f"Appointments for {doctor_name}:\n" + "\n".join(lines)



def appointment_booking(
    doctor_name: str,
    appointment_date: DateType,
    appointment_time: TimeType,
    patient_id: str = None
) -> str:
    """
    Books an appointment after checking doctor availability.
    """
    try:
        # patient_id = current_user.get("patient_id")
        logger.info(f"finding patientid {patient_id}")

        session = get_db()
        logger.info("finding patientid {patient_id}")

        # 1️⃣ Find active doctor
        doctor = (
            session.query(DoctorORM)
            .filter(
                DoctorORM.name.ilike(f"%{doctor_name}%"),
                DoctorORM.is_active.is_(True)
            )
            .first()
        )

        if not doctor:
            return f"No active doctor found with name '{doctor_name}'"

        # 2️⃣ Check availability
        existing_appointment = (
            session.query(AppointmentORM)
            .filter(
                AppointmentORM.doctor_id == str(doctor.id),
                AppointmentORM.appointment_date == appointment_date,
                AppointmentORM.appointment_time == appointment_time,
                AppointmentORM.status.in_([
                    AppointmentStatus.booked,
                    AppointmentStatus.confirmed
                ])
            )
            .first()
        )

        if existing_appointment:
            return (
                f" Dr. {doctor.name} is not available on "
                f"{appointment_date} at {appointment_time}"
            )

        # 3️⃣ Confirm (book) appointment
        appointment = AppointmentORM(
            doctor_id=str(doctor.id),
            patient_id=patient_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status=AppointmentStatus.confirmed
        )

        session.add(appointment)
        session.commit()

        return (
            f"✅ Appointment confirmed with Dr. {doctor.name} "
            f"on {appointment_date} at {appointment_time}"
        )

    except IntegrityError:
        session.rollback()
        return (
            f" Slot conflict detected for Dr. {doctor_name} "
            f"on {appointment_date} at {appointment_time}"
        )

    except Exception as e:
        session.rollback()
        logger.error(f"error in the appointment booking {e}")
        return f" Failed to book appointment: {str(e)}"

    finally:
        session.close()
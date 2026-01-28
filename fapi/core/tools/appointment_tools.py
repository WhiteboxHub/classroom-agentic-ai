from google.adk.tools import FunctionTool


from pydantic import BaseModel
from typing import Optional
from ..utils.data_queries.get_data import appointment_list,appointment_booking
from datetime import date as DateType, time as TimeType

class appointment_tools:
    @staticmethod
    def appointment_booking(doctor_name: str, date: DateType, time: TimeType) -> str:
        """Books an appointment with the specified doctor.
        Args:
            doctor_name: The name of the doctor.
            date: The date of the appointment.
            time: The time of the appointment.
            
        Returns:
            The status of the appointment booking.
        """
        try:
           res =  appointment_booking(doctor_name,date,time)
        except Exception as e:
            print(f"the eroror in app booking {e}")
            return "error occured while booking {e}"
        return res

    @staticmethod
    def appointment_cancellation(doctor_name: str, date: str, time: str) -> str:
        """Cancels an appointment with the specified doctor.
        
        Args:
            doctor_name: The name of the doctor.
            date: The date of the appointment.
            time: The time of the appointment.
            
        Returns:
            The status of the appointment cancellation.
        """
        return f"Appointment cancelled with {doctor_name} on {date} at {time}"

    @staticmethod
    def appointment_rescheduling(doctor_name: str, date: str, time: str) -> str:
        """Reschedules an appointment with the specified doctor.
        
        Args:
            doctor_name: The name of the doctor.
            date: The date of the appointment.
            time: The time of the appointment.
            
        Returns:
            The status of the appointment rescheduling.
        """
        return f"Appointment rescheduled with {doctor_name} on {date} at {time}"

    @staticmethod
    def appointment_confirmation(doctor_name: str, date: str, time: str) -> str:
        """Confirms an appointment with the specified doctor.
        
        Args:
            doctor_name: The name of the doctor.
            date: The date of the appointment.
            time: The time of the appointment.
            
        Returns:
            The status of the appointment confirmation.
        """
        return f"Appointment confirmed with {doctor_name} on {date} at {time}"

    @staticmethod
    def appointment_reminder(doctor_name: str, date: str, time: str) -> str:
        """Sends a reminder for an appointment with the specified doctor. 
        
        Args:
            doctor_name: The name of the doctor.
            date: The date of the appointment.
            time: The time of the appointment.
            
        Returns:
            The status of the appointment reminder.
        """
        return f"Appointment reminder sent for {doctor_name} on {date} at {time}"

    @staticmethod
    def appointment_list(doctor_name: str) -> str:
        """Lists all appointments for the specified doctor.
        
        Args:
            doctor_name: The name of the doctor.
            
        Returns:
            The list of appointments for the specified doctor.
        """
        try:
            print(f"appointment list is called")
            data = appointment_list(doctor_name)
        except Exception as e:
            print(f"appointment list failed with error {e}")
            return str(e)
        

        return data
    
    def get_tools(self):
        return [
            FunctionTool(self.appointment_booking), 
            FunctionTool(self.appointment_cancellation),
            FunctionTool(self.appointment_rescheduling),
            FunctionTool(self.appointment_confirmation),
            FunctionTool(self.appointment_reminder),
            FunctionTool(self.appointment_list),
        ]

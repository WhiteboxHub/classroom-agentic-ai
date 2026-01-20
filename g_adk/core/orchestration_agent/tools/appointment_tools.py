from google.adk.tools import FunctionTool

class appointment_tools:
    @staticmethod
    def appointment_booking(doctor_name: str, date: str, time: str) -> str:
        """Books an appointment with the specified doctor.
        
        Args:
            doctor_name: The name of the doctor.
            date: The date of the appointment.
            time: The time of the appointment.
            
        Returns:
            The status of the appointment booking.
        """
        return f"Appointment booked with {doctor_name} on {date} at {time}"

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
        return f"Appointments for {doctor_name}: {['appointment1', 'appointment2', 'appointment3']}"
    
    def get_tools(self):
        return [
            FunctionTool(self.appointment_booking), 
            FunctionTool(self.appointment_cancellation),
            FunctionTool(self.appointment_rescheduling),
            FunctionTool(self.appointment_confirmation),
            FunctionTool(self.appointment_reminder),
            FunctionTool(self.appointment_list),
        ]

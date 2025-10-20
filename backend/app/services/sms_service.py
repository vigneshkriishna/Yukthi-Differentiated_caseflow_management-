"""
SMS Service for Critical Notifications
"""
import os
from typing import Optional

class SMSService:
    def __init__(self):
        # Twilio configuration
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # AWS SNS alternative
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-west-2")
    
    def send_urgent_notification(self, phone_number: str, case_number: str, message: str) -> bool:
        """Send urgent SMS notifications"""
        sms_text = f"DCM URGENT: Case {case_number} - {message}"
        return self._send_sms(phone_number, sms_text)
    
    def send_hearing_reminder_sms(self, phone_number: str, case_number: str, 
                                date: str, time: str) -> bool:
        """Send hearing reminder via SMS"""
        sms_text = f"DCM Reminder: Case {case_number} hearing on {date} at {time}. Please attend."
        return self._send_sms(phone_number, sms_text)
    
    def _send_sms(self, phone_number: str, message: str) -> bool:
        """Internal SMS sending method"""
        try:
            if self.twilio_account_sid and self.twilio_auth_token:
                return self._send_via_twilio(phone_number, message)
            elif self.aws_access_key and self.aws_secret_key:
                return self._send_via_aws_sns(phone_number, message)
            else:
                print("No SMS service configured")
                return False
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return False
    
    def _send_via_twilio(self, phone_number: str, message: str) -> bool:
        """Send SMS via Twilio"""
        try:
            from twilio.rest import Client
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            message = client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=phone_number
            )
            return message.sid is not None
        except ImportError:
            print("Twilio library not installed. Run: pip install twilio")
            return False
    
    def _send_via_aws_sns(self, phone_number: str, message: str) -> bool:
        """Send SMS via AWS SNS"""
        try:
            import boto3
            
            sns_client = boto3.client(
                'sns',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            
            response = sns_client.publish(
                PhoneNumber=phone_number,
                Message=message
            )
            return response['ResponseMetadata']['HTTPStatusCode'] == 200
        except ImportError:
            print("Boto3 library not installed. Run: pip install boto3")
            return False

# Global SMS service instance
sms_service = SMSService()
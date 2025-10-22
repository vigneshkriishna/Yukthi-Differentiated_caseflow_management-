"""
Email Service for Notifications
Enhanced with HTML templates and multiple provider support
"""
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List

from jinja2 import Template


class EmailService:
    def __init__(self):
        # Email configuration from environment
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)

        # SendGrid alternative
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")

        # Email templates
        self.templates = {
            "case_filed": {
                "subject": "Case Filed Successfully - {case_number}",
                "template": """
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c5aa0;">Case Filed Successfully</h2>
                        <p>Dear {user_name},</p>
                        <p>Your case has been filed successfully in the Digital Case Management System.</p>

                        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #2c5aa0; margin: 20px 0;">
                            <h3>Case Details:</h3>
                            <p><strong>Case Number:</strong> {case_number}</p>
                            <p><strong>Case Title:</strong> {case_title}</p>
                            <p><strong>Case Type:</strong> {case_type}</p>
                            <p><strong>Filing Date:</strong> {filing_date}</p>
                            <p><strong>Status:</strong> {status}</p>
                        </div>

                        <p>You will receive further notifications as your case progresses through the system.</p>

                        <p>Best regards,<br>
                        Digital Case Management System</p>
                    </div>
                </body>
                </html>
                """
            },
            "hearing_scheduled": {
                "subject": "Hearing Scheduled - Case {case_number}",
                "template": """
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #28a745;">Hearing Scheduled</h2>
                        <p>Dear {user_name},</p>
                        <p>A hearing has been scheduled for your case. Please mark your calendar and be present on time.</p>

                        <div style="background-color: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                            <h3>Hearing Details:</h3>
                            <p><strong>Case Number:</strong> {case_number}</p>
                            <p><strong>Hearing Date:</strong> {hearing_date}</p>
                            <p><strong>Hearing Time:</strong> {hearing_time}</p>
                            <p><strong>Court:</strong> {court_name}</p>
                            <p><strong>Judge:</strong> {judge_name}</p>
                        </div>

                        <p><strong>Important:</strong> Please arrive at least 15 minutes before the scheduled time.</p>

                        <p>Best regards,<br>
                        Digital Case Management System</p>
                    </div>
                </body>
                </html>
                """
            },
            "status_update": {
                "subject": "Case Status Update - {case_number}",
                "template": """
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #ffc107;">Case Status Updated</h2>
                        <p>Dear {user_name},</p>
                        <p>The status of your case has been updated in the system.</p>

                        <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                            <h3>Update Details:</h3>
                            <p><strong>Case Number:</strong> {case_number}</p>
                            <p><strong>Previous Status:</strong> {previous_status}</p>
                            <p><strong>New Status:</strong> {new_status}</p>
                            <p><strong>Updated On:</strong> {update_date}</p>
                            {notes}
                        </div>

                        <p>You can log into the system to view more details about your case.</p>

                        <p>Best regards,<br>
                        Digital Case Management System</p>
                    </div>
                </body>
                </html>
                """
            },
            "bns_suggestion": {
                "subject": "BNS Section Suggestions Available - Case {case_number}",
                "template": """
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #6f42c1;">BNS Section Suggestions</h2>
                        <p>Dear {user_name},</p>
                        <p>AI-powered BNS (Bharatiya Nyaya Sanhita) section suggestions are now available for your case.</p>

                        <div style="background-color: #f8f9ff; padding: 15px; border-left: 4px solid #6f42c1; margin: 20px 0;">
                            <h3>Suggestion Details:</h3>
                            <p><strong>Case Number:</strong> {case_number}</p>
                            <p><strong>Suggested Sections:</strong> {suggested_sections}</p>
                            <p><strong>Confidence Score:</strong> {confidence}%</p>
                        </div>

                        <p>Please review these suggestions and consult with your legal advisor.</p>

                        <p>Best regards,<br>
                        Digital Case Management System</p>
                    </div>
                </body>
                </html>
                """
            }
        }

    def send_case_notification(self, to_email: str, user_name: str,
                             notification_type: str, case_data: Dict[str, Any]) -> bool:
        """Send case-related notifications with proper templates"""
        if notification_type not in self.templates:
            print(f"Unknown notification type: {notification_type}")
            return False

        template_data = self.templates[notification_type]
        subject = template_data["subject"].format(**case_data)

        # Prepare template variables
        template_vars = {
            "user_name": user_name,
            **case_data
        }

        # Render HTML template
        html_template = Template(template_data["template"])
        html_body = html_template.render(**template_vars)

        return self._send_email(to_email, subject, html_body, is_html=True)

    def send_hearing_reminder(self, to_email: str, user_name: str,
                            case_number: str, hearing_date: str,
                            hearing_time: str, court_name: str = "Main Court",
                            judge_name: str = "Honorable Judge") -> bool:
        """Send hearing reminder notifications"""
        case_data = {
            "case_number": case_number,
            "hearing_date": hearing_date,
            "hearing_time": hearing_time,
            "court_name": court_name,
            "judge_name": judge_name
        }

        return self.send_case_notification(to_email, user_name, "hearing_scheduled", case_data)

    def send_status_update(self, to_email: str, user_name: str,
                          case_number: str, previous_status: str,
                          new_status: str, notes: str = "") -> bool:
        """Send case status update notifications"""
        case_data = {
            "case_number": case_number,
            "previous_status": previous_status,
            "new_status": new_status,
            "update_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "notes": f"<p><strong>Notes:</strong> {notes}</p>" if notes else ""
        }

        return self.send_case_notification(to_email, user_name, "status_update", case_data)

    def send_bns_suggestions(self, to_email: str, user_name: str,
                           case_number: str, suggested_sections: List[str],
                           confidence: float) -> bool:
        """Send BNS section suggestions"""
        case_data = {
            "case_number": case_number,
            "suggested_sections": ", ".join(suggested_sections),
            "confidence": round(confidence * 100, 1)
        }

        return self.send_case_notification(to_email, user_name, "bns_suggestion", case_data)

    async def send_case_created_notification(self, case, created_by_user: str):
        """Send notification when a new case is created"""
        try:
            # Determine recipients
            recipients = []

            # Add case assigned clerk if available
            if hasattr(case, 'assigned_clerk') and case.assigned_clerk:
                recipients.append({
                    "email": case.assigned_clerk.email,
                    "name": case.assigned_clerk.full_name,
                    "role": "Assigned Clerk"
                })

            # Add case assigned judge if available
            if hasattr(case, 'assigned_judge') and case.assigned_judge:
                recipients.append({
                    "email": case.assigned_judge.email,
                    "name": case.assigned_judge.full_name,
                    "role": "Assigned Judge"
                })

            # Add FIR complainant if available
            if hasattr(case, 'complainant_email') and case.complainant_email:
                recipients.append({
                    "email": case.complainant_email,
                    "name": case.complainant_name or "Complainant",
                    "role": "Complainant"
                })

            # Prepare email template data
            template_data = {
                "case_number": case.case_number,
                "case_id": case.id,
                "synopsis": case.synopsis,
                "status": case.status,
                "created_by": created_by_user,
                "created_date": "now"
            }

            # Send notifications to all recipients
            success_count = 0
            for recipient in recipients:
                if self._send_template_email(
                    to_email=recipient["email"],
                    template_name="case_created",
                    template_data={**template_data, "recipient_name": recipient["name"], "recipient_role": recipient["role"]},
                    subject=f"New Case Created: {case.case_number}"
                ):
                    success_count += 1

            print(f"✅ Case creation notification sent to {success_count}/{len(recipients)} recipients")
            return success_count > 0

        except Exception as e:
            print(f"❌ Failed to send case creation notification: {e}")
            return False

    async def send_case_status_update_notification(self, case, old_status: str, new_status: str, updated_by_user: str):
        """Send notification when case status is updated"""
        try:
            # Determine recipients (same logic as case creation)
            recipients = []

            if hasattr(case, 'assigned_clerk') and case.assigned_clerk:
                recipients.append({
                    "email": case.assigned_clerk.email,
                    "name": case.assigned_clerk.full_name,
                    "role": "Assigned Clerk"
                })

            if hasattr(case, 'assigned_judge') and case.assigned_judge:
                recipients.append({
                    "email": case.assigned_judge.email,
                    "name": case.assigned_judge.full_name,
                    "role": "Assigned Judge"
                })

            if hasattr(case, 'complainant_email') and case.complainant_email:
                recipients.append({
                    "email": case.complainant_email,
                    "name": case.complainant_name or "Complainant",
                    "role": "Complainant"
                })

            # Prepare email template data
            template_data = {
                "case_number": case.case_number,
                "case_id": case.id,
                "synopsis": case.synopsis[:200] + "..." if len(case.synopsis) > 200 else case.synopsis,
                "old_status": old_status.replace("_", " ").title(),
                "new_status": new_status.replace("_", " ").title(),
                "updated_by": updated_by_user,
                "updated_date": "now"
            }

            # Send notifications to all recipients
            success_count = 0
            for recipient in recipients:
                if self._send_template_email(
                    to_email=recipient["email"],
                    template_name="case_updated",
                    template_data={**template_data, "recipient_name": recipient["name"], "recipient_role": recipient["role"]},
                    subject=f"Case Status Updated: {case.case_number}"
                ):
                    success_count += 1

            print(f"✅ Case status update notification sent to {success_count}/{len(recipients)} recipients")
            return success_count > 0

        except Exception as e:
            print(f"❌ Failed to send case status update notification: {e}")
            return False

    def _send_template_email(self, to_email: str, template_name: str, template_data: dict, subject: str) -> bool:
        """Send email using HTML template"""
        try:
            # Load and render template
            template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "emails", f"{template_name}.html")

            if not os.path.exists(template_path):
                print(f"❌ Template not found: {template_path}")
                return False

            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # Simple template rendering (replace placeholders)
            html_body = template_content
            for key, value in template_data.items():
                placeholder = "{{ " + key + " }}"
                html_body = html_body.replace(placeholder, str(value))

            # Send the email
            return self._send_email(to_email, subject, html_body, is_html=True)

        except Exception as e:
            print(f"❌ Failed to send template email: {e}")
            return False

    async def send_bns_suggestions_notification(self, case, suggestions, generated_by_user: str, case_updated: bool = False):
        """Send notification when BNS suggestions are generated for a case"""
        try:
            # Prepare suggestion data for template
            suggestion_list = []
            for suggestion in suggestions:
                if hasattr(suggestion, 'to_dict'):
                    suggestion_list.append(suggestion.to_dict())
                else:
                    suggestion_list.append({
                        "section": str(suggestion),
                        "confidence": "N/A",
                        "description": "BNS Section Suggestion"
                    })

            # Determine recipients
            recipients = []

            # Add case assigned clerk if available
            if hasattr(case, 'assigned_clerk') and case.assigned_clerk:
                recipients.append({
                    "email": case.assigned_clerk.email,
                    "name": case.assigned_clerk.full_name,
                    "role": "Assigned Clerk"
                })

            # Add case assigned judge if available
            if hasattr(case, 'assigned_judge') and case.assigned_judge:
                recipients.append({
                    "email": case.assigned_judge.email,
                    "name": case.assigned_judge.full_name,
                    "role": "Assigned Judge"
                })

            # Add FIR complainant if available
            if hasattr(case, 'complainant_email') and case.complainant_email:
                recipients.append({
                    "email": case.complainant_email,
                    "name": case.complainant_name or "Complainant",
                    "role": "Complainant"
                })

            # Prepare email template data
            template_data = {
                "case_number": case.case_number,
                "case_id": case.id,
                "synopsis": case.synopsis[:200] + "..." if len(case.synopsis) > 200 else case.synopsis,
                "suggestions": suggestion_list,
                "total_suggestions": len(suggestion_list),
                "generated_by": generated_by_user,
                "case_updated": case_updated,
                "update_status": "Case has been updated with these suggestions" if case_updated else "Case remains unchanged"
            }

            # Send notifications to all recipients
            success_count = 0
            for recipient in recipients:
                if self._send_template_email(
                    to_email=recipient["email"],
                    template_name="bns_suggestions",
                    template_data={**template_data, "recipient_name": recipient["name"], "recipient_role": recipient["role"]},
                    subject=f"BNS Suggestions Generated for Case {case.case_number}"
                ):
                    success_count += 1

            print(f"✅ BNS suggestions notification sent to {success_count}/{len(recipients)} recipients")
            return success_count > 0

        except Exception as e:
            print(f"❌ Failed to send BNS suggestions notification: {e}")
            return False

    def _send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Internal method to send email"""
        try:
            if self.sendgrid_api_key:
                return self._send_via_sendgrid(to_email, subject, body, is_html)
            elif self.smtp_username and self.smtp_password:
                return self._send_via_smtp(to_email, subject, body, is_html)
            else:
                print("❌ No email service configured. Please set up SMTP or SendGrid credentials.")
                return False
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

    def _send_via_smtp(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()

            print(f"✅ Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"❌ SMTP Error: {e}")
            return False

    def _send_via_sendgrid(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email via SendGrid API"""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail

            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=body if is_html else None,
                plain_text_content=body if not is_html else None
            )

            response = sg.send(message)
            success = response.status_code == 202

            if success:
                print(f"✅ SendGrid email sent successfully to {to_email}")
            else:
                print(f"❌ SendGrid error: {response.status_code}")

            return success

        except Exception as e:
            print(f"❌ SendGrid Error: {e}")
            return False

    def test_email_configuration(self) -> bool:
        """Test email configuration"""
        print("🔍 Testing email configuration...")

        if self.sendgrid_api_key:
            print("✅ SendGrid API key found")
            return True
        elif self.smtp_username and self.smtp_password:
            print("✅ SMTP credentials found")
            print(f"   Host: {self.smtp_host}:{self.smtp_port}")
            print(f"   Username: {self.smtp_username}")
            return True
        else:
            print("❌ No email service configured")
            print("   Please set either:")
            print("   1. SENDGRID_API_KEY for SendGrid")
            print("   2. SMTP_USERNAME and SMTP_PASSWORD for SMTP")
            return False

# Global email service instance
email_service = EmailService()

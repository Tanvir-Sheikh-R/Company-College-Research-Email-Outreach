import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Tuple

class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, email: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password

    def send_email(self, to_email: str, subject: str, body: str) -> Tuple[bool, str]:
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.email
            msg["To"] = to_email
            msg["Subject"] = subject

            part = MIMEText(body, "plain")
            msg.attach(part)

            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.email, self.password)
                server.sendmail(self.email, to_email, msg.as_string())

            return True, "sent"
        except smtplib.SMTPAuthenticationError:
            return False, "auth_failed"
        except smtplib.SMTPRecipientsRefused:
            return False, "recipient_refused"
        except Exception as e:
            return False, str(e)

    def send_bulk(self, recipients: List[Dict], subject: str, body_template: str) -> List[Dict]:
        results = []
        for r in recipients:
            personalized_body = body_template.replace("{{company}}", r.get("name", ""))
            success, msg = self.send_email(r["email"], subject, personalized_body)
            results.append({
                "email": r["email"],
                "company": r.get("name", ""),
                "success": success,
                "message": msg,
            })
        return results

import json
import smtplib
from email.message import EmailMessage

from decouple import config

from theralogs.utils import render_to_pdf


class email_manager:
    @classmethod
    def send_email(cls, session):
        msg = EmailMessage()
        msg["Subject"] = "Testing out theralogs email from Namecheap!"
        msg["From"] = config("NAMECHEAP_EMAIL")
        msg["To"] = session.patient.email

        context = {
            "transcript": json.loads(session.recording_json),
            "date_created": session.created_at,
            "therapist": session.patient.therapist.name,
            "patient": session.patient.name,
        }

        pdf = render_to_pdf(context)
        msg.add_attachment(
            pdf, maintype="application", subtype="octet-stream", filename="patient.pdf"
        )

        with smtplib.SMTP_SSL("mail.privateemail.com", 465) as smtp:
            smtp.login(config("NAMECHEAP_EMAIL"), config("NAMECHEAP_PASSWORD"))
            smtp.send_message(msg)

import smtplib
from email.message import EmailMessage

from decouple import config

from theralogs.managers.audio_transcribe_manager import audio_transcribe_manager
from theralogs.utils import render_to_pdf, format_transcript_utterances


class email_manager:
    @classmethod
    def send_email(cls, session):
        msg = EmailMessage()
        msg[
            "Subject"
        ] = f"your audio transcription with {session.patient.therapist.name}"
        msg["From"] = config("NAMECHEAP_EMAIL")
        msg["To"] = session.patient.email

        response_json = audio_transcribe_manager.get_transcript(
            transcript_id=session.transcript_id
        )

        utterances = response_json["utterances"]
        formatted_transcript = format_transcript_utterances(utterances)

        context = {
            "transcript": formatted_transcript,
            "date_created": session.created_at,
        }

        pdf = render_to_pdf(context)
        msg.add_attachment(
            pdf,
            maintype="application",
            subtype="octet-stream",
            filename="transcription.pdf",
        )

        with smtplib.SMTP_SSL("mail.privateemail.com", 465) as smtp:
            smtp.login(config("NAMECHEAP_EMAIL"), config("NAMECHEAP_PASSWORD"))
            smtp.send_message(msg)

    @classmethod
    def send_contact_us_email(cls, dict):
        msg = EmailMessage()
        msg["Subject"] = f"{dict['name']} - {dict['email']} asked a question"
        msg["From"] = config("NAMECHEAP_EMAIL")
        msg["To"] = config("NAMECHEAP_EMAIL")
        msg.set_content(dict["question"])

        with smtplib.SMTP_SSL("mail.privateemail.com", 465) as smtp:
            smtp.login(config("NAMECHEAP_EMAIL"), config("NAMECHEAP_PASSWORD"))
            smtp.send_message(msg)

    @classmethod
    def send_new_customer_notification(cls, dict):
        msg = EmailMessage()
        msg["Subject"] = "New user registered"
        msg["From"] = config("NAMECHEAP_EMAIL")
        msg["To"] = config("NAMECHEAP_EMAIL")
        msg.set_content(
            f"{dict['name']} - {dict['email']} just registered as a new customer"
        )

        with smtplib.SMTP_SSL("mail.privateemail.com", 465) as smtp:
            smtp.login(config("NAMECHEAP_EMAIL"), config("NAMECHEAP_PASSWORD"))
            smtp.send_message(msg)

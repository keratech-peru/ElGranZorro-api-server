from app.config import Email
from email.message import EmailMessage
import smtplib

def send_email(msg: str, addressee: str, asunto: str) -> None:
    remitente = Email.REMITENTE
    destinatario = addressee
    mensaje = msg
    email = EmailMessage()
    email["From"] = remitente
    email["To"] = destinatario
    email["Subject"] = asunto
    # email.set_content(mensaje, subtype="html")
    email.set_content(mensaje)
    smtp = smtplib.SMTP_SSL("smtp.gmail.com")
    smtp.login(remitente, Email.PASSWORD)
    smtp.sendmail(remitente, destinatario, email.as_string())
    smtp.quit()
from app.config import Email, Whatsapp
from app.notifications.constants import TextToSend
from email.message import EmailMessage
import smtplib
import requests

class Notificaciones_:
    @staticmethod
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

    @staticmethod
    def send_whatsapp(phone: str, message: str) -> None:
        body = {"message":message,"phone":'51'+phone}
        response = requests.post(Whatsapp.URL_SEND, json = body)
        #print(response.text)
        #print(response.status_code)
    
    def send_whatsapp_otp(phone: str, otp: str) -> None:
        Notificaciones_.send_whatsapp(phone, TextToSend.OTP + '*' + otp + '*')
from app.tournaments.models import Tournaments

OTP_DIGIT_LIMIT = 4
URL_FRONT = "https://egz-frontend.vercel.app/"
class TextToSend:
    def welcome():
        text = f"Bienvenido a *El Gran Zorro*🐺, gracias por completar tu registro.\nRecuerda visitar nuestra pagina {URL_FRONT}"
        return text 
    
    def otp(otp:str):
        text = f"Tu codigo de activacion es *{otp}*"
        return text

    def enrollment(tournament:Tournaments, name: str):
        text = f'''Hola😁 {name} , estas inscrito al torneo *{tournament.name}* con fecha de inicio *{tournament.start_date}*. 
                \nPodras realizar tus jugadas en el siguiente enlace:\n\n{URL_FRONT}/tournament/{tournament.id}'''
        return text
    
    def declining(tournament:Tournaments, name: str):
        text = f''' Hola {name} 😓, nos apena la decision que tomaste
                    \nDeclinaste del torneo {tournament.name}
                    Puedes probar suerte en otros torneos y ganar 💵💵💵\n
                    {URL_FRONT}/tournaments
                '''
        return text
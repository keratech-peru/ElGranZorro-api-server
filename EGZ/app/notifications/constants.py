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
        text = f'''Hola *{name}* 😁, estas inscrito al torneo *{tournament.name}* con fecha de inicio *{tournament.start_date}*. 
                \nPodras realizar tus jugadas en el siguiente enlace:\n\n{URL_FRONT}/tournament/{tournament.id}'''
        return text
    
    def declining(tournament:Tournaments, name: str):
        text = f''' Hola *{name}* 👻, nos apena la decision que tomaste💔.\n
                    Declinaste del torneo {tournament.name}, puedes probar suerte en otros torneos y ganar 💸💰💵\n
                    {URL_FRONT}/tournaments
                '''
        return text
    
    def eliminated(tournament:Tournaments, name: str, fase: str):
        text = f''' Hola *{name}* 😖, fuiste eliminado del torneo *{tournament.name}* en la fase de *{fase}*.
                \n✅ Puedes revisar los resultados  en {URL_FRONT}/tournament/{tournament.id}
                \n✅ Puedes probar suerte en otros torneos y ganar 💰💰💰 en {URL_FRONT}/tournaments
                '''
        return text
    
    def stage_passed(tournament:Tournaments, name: str, fase: str):
        text = f''' Hola *{name}* 😁.Felicidades!!🎉, estas un paso mas cerca del premio 💸💰💵,superaste la fase de *{fase}* del torneo *{tournament.name}*.
                \n✅ Puedes revisar los resultados  en {URL_FRONT}/tournament/{tournament.id}\n  
                '''
        return text

    def user_not_play_games(tournament:Tournaments, name: str, fase: str, number_play_games: str):
        text = f''' Hola *{name}* 😣. Observamos que no completaste tus jugadas en la fase de *{fase}* partido {number_play_games} del torneo *{tournament.name}*.
                No te pierdas la oportunidad de ganar 💸💰💵.
                \n✅ Realiza tus jugadas en {URL_FRONT}/tournament/{tournament.id}\n  
                '''
        return text
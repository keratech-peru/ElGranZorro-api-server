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

    def user_not_play_games(tournament:Tournaments, name: str, stage: str):
        text = f''' Hola *{name}* 😣. Observamos que no completaste tus jugadas en la fase de *{stage}* del torneo *{tournament.name}*. No te pierdas la oportunidad de ganar 💸💰💵.
                \n✅ Realiza tus jugadas en {URL_FRONT}/tournament/{tournament.id}\n
                '''
        return text

    def user_winner(tournament:Tournaments, name: str):
        text = f''' Hola *{name}* 😜 Felicidades !!! 🎉💰. Eres el ganador del torneo *{tournament.name}*. Contacta al area financiera mediante el whatsapp (+51 910 034 199) para reclamar tu premio 💸💰💵.
                \n✅ Recuerda que puedes participar de otros torneos en {URL_FRONT}/tournament\n
                '''
        return text
    
    def user_equal_poitns(tournament:Tournaments, name1: str, name2:str,list_date_1, list_date_2, stage: str):
        text_data = ""
        for i in range(len(list_date_1)):
            text_data = text_data + f"\n✅ (*{name1}*){list_date_1[i][0].strftime('%d/%m/%Y %H:%M')} - {list_date_2[i][0].strftime('%d/%m/%Y %H:%M')}(*{name2}*)"
        text = f''' Hola *{name1}* 👀. Empataste con el usuario *{name2}* en la fase de *{stage}* del torneo *{tournament.name}*. El desempate se decide por quien fue el primero en completar sus resultado por emfrentamiento.
                
                \n✅ Para mas detalle revisa el torneo : {URL_FRONT}/tournament/{tournament.id}\n
                '''
        return text+text_data
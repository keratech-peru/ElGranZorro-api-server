from app.tournaments.models import Tournaments, FootballGames

OTP_DIGIT_LIMIT = 4
URL_FRONT = "https://egz-frontend-alpha.vercel.app/"
class TextToSend:
    def login():
        text = f"Bienvenido a *El Gran Zorro*🐺, tu session esta activa.\nRecuerda visitar nuestra pagina {URL_FRONT}"
        return text 
    
    def otp(otp:str):
        text = f"Tu codigo de activacion es *{otp}*"
        return text

    def enrollment(tournament:Tournaments, name: str):
        text = f'''Hola *{name}* 😁, estas inscrito al torneo *{tournament.name}* con fecha de inicio *{tournament.start_date}*. 
                \nPodras realizar tus jugadas en el siguiente enlace:\n\n{URL_FRONT}tournament/{tournament.id}'''
        return text
    
    def declining(tournament:Tournaments, name: str):
        text = f''' Hola *{name}* 👻, nos apena la decision que tomaste💔.
                    \nDeclinaste del torneo {tournament.name}, puedes probar suerte en otros torneos y ganar 💸💰💵
                    \n{URL_FRONT}/tournaments\n
                    \nPD. El equipo financiero se contactara contigo para proceder con el desembolso.
                '''
        return text
    
    def eliminated(tournament:Tournaments, name: str, fase: str):
        text = f''' Hola *{name}* 😖, fuiste eliminado del torneo *{tournament.name}* en la fase de *{fase}*.
                \n✅ Puedes revisar los resultados  en {URL_FRONT}tournament/{tournament.id}
                \n✅ Puedes probar suerte en otros torneos y ganar 💰💰💰 en {URL_FRONT}/tournaments
                '''
        return text
    
    def stage_passed(tournament:Tournaments, name: str, fase: str):
        text = f''' Hola *{name}* 😁.Felicidades!!🎉, estas un paso mas cerca del premio 💸💰💵,superaste la fase de *{fase}* del torneo *{tournament.name}*.
                \n✅ Puedes revisar los resultados  en {URL_FRONT}tournament/{tournament.id}\n  
                '''
        return text

    def user_not_play_games(tournament:Tournaments, name: str, stage: str):
        text = f''' Hola *{name}* 😣. Observamos que no completaste tus jugadas en la fase de *{stage}* del torneo *{tournament.name}*. No te pierdas la oportunidad de ganar 💸💰💵.
                \n✅ Realiza tus jugadas en {URL_FRONT}tournament/{tournament.id}\n
                '''
        return text

    def user_winner(tournament:Tournaments, name: str):
        text = f''' Hola *{name}* 😜 Felicidades !!! 🎉💰. Eres el ganador del torneo *{tournament.name}*. Contacta al area financiera mediante el whatsapp (+51 910 034 199) para reclamar tu premio 💸💰💵.
                \n✅ Recuerda que puedes participar de otros torneos en {URL_FRONT}/tournament\n
                '''
        return text
    
    def user_equal_poitns(tournament:Tournaments, name1: str, name2:str,list_date_1, list_date_2, stage: str):
        text = f''' Hola *{name1}* 👀. Empataste con el usuario *{name2}* en la fase de *{stage}* del torneo *{tournament.name}*. El desempate se decide por quien fue el primero en completar sus resultado por emfrentamiento.
                \n✅ (*{name1}*){list_date_1[0][0].strftime('%d/%m/%Y %H:%M')} - {list_date_2[0][0].strftime('%d/%m/%Y %H:%M')}(*{name2}*)
                \n✅ Para mas detalle revisa el torneo : {URL_FRONT}tournament/{tournament.id}
                '''
        return text
    
    def user_has_not_played(footballgame:FootballGames, name: str):
        text = f''' Hola *{name}* 👀. Te recordamos que falta menos de *1 hora* ⏰ para que inicie el partido de *{footballgame.home_team} - {footballgame.away_team}* correspondiente a la *{footballgame.tournament_stage}* del torneo *{footballgame.tournament.name}*.   
                \n✅ Recuerda *realizar tu jugada* antes del comienzo del partido ⏳ en {URL_FRONT}tournament/{footballgame.tournament_id}\n
                '''
        return text

    def user_commission_agent(name: str):
        text = f''' Hola *{name}* 👀.Gracias por colaborar con nosotros, en unos minutos un asesor se contactara contigo para explicarte los por menores.   
                \n✅ Recuerda estar atento a los nuevos torneos {URL_FRONT}tournaments\n
                '''
        return text
    
    def user_without_completing_play(name: str):
        text = f''' Hola *{name}*.Tu contrincante ni tu completo ninguna de sus jugadas. El ganador se definira al azar, suerte.\n
                '''
        return text        
  
class Otp:
    COUNT = 5
    MINUTES = 10
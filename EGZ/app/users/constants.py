from app.notifications.constants import Otp
from app.tournaments.constants import STATUS_TOURNAMENT

class ErrorCode:
    EMAIL_ALREADY_USED = "No se puede crear el usuario, por que el correo ya se ha utilizado."
    PHONE_ALREADY_USED = "No se puede crear el usuario, por que el phone ya se ha utilizado."
    TEMPORARILY_BLOCKED = f"Usuario bloqueado por los proximos {Otp.MINUTES} minutos"
    INCORRECT_OTP = "Codigo invalido!, intentelo otra vez"
    EMAIL_CANNOT_UPDATE = "No se puede actualiza el correo, ya está registrado"
    PHONE_CANNOT_UPDATE = "No se puede actualiza el celular, ya está registrado"
    EMAIL_UNREGISTERED = " Email no registrado."
    USER_ALREADY_REGISTERED = "El Usurio ya esta registrado en el torneo"
    USER_ALREADY_NOT_REGISTERED = "El Usurio no estan inscrito en el torneo"
    USER_CANNOT_TOURNAMENT_ALREADY_STARTED = "El usuario no puede retirarse del torneo, ya empezo"
    USER_NOT_ENROLLMEND_IN_THAT_TOURNAMENT = "Usuario no esta inscrito a ese torneo"
    USER_NOT_REGISTERED_IN_THAT_FOOTBALLGAME = "Usuario no esta registrado para esa jugada"
    USER_MAX_ATTEMPS_VALIDATE_PASSWORD_UPDATE = "Error en la validacion, se supero el maximo de intentos. Vuelve a intentarlo en 30 min."
    USER_FAILED_VALIDATE_PASSWORD_UPDATE = "Error en la recuperacion de la contraseña, los valores ingresados no son los correctos."
    OPTION_NOT_ALLOWED = "Opcion no permitida"
    USER_ALREADY_COMMISSION_AGENT = "El usuario ya fue registrado como un agente comisionado."
    INVALID_COUPON = "Cupon invalido, prueba con otro."
    EXPIRED_COUPON = "El cupon expiro."

USER_STATUS_IN_TOURNAMENT = {
    "EE": STATUS_TOURNAMENT["EE"],
    "EP": "EN PROCESO",
    "EGP": "ELIMINADO - " + STATUS_TOURNAMENT["GP"],
    "EOC": "ELIMINADO - " + STATUS_TOURNAMENT["OC"],
    "ECU": "ELIMINADO - " + STATUS_TOURNAMENT["CU"],
    "ESF": "ELIMINADO - " + STATUS_TOURNAMENT["SF"],
    "EFI": "ELIMINADO - " + STATUS_TOURNAMENT["FI"],
    "GA": "GANADOR"
}

class Coupon:
    DURATION = 7
    PERCENT = 20

from app.notifications.constants import Otp

class ErrorCode:
    EMAIL_ALREADY_USED = "No se puede crear el usuario, por que el correo ya se ha utilizado."
    PHONE_ALREADY_USED = "No se puede crear el usuario, por que el phone ya se ha utilizado."
    TEMPORARILY_BLOCKED = f"Usuario bloqueado por los proximos {Otp.MINUTES} minutos"
    INCORRECT_OTP = "Codigo invalido!, intentelo otra vez"
    EMAIL_CANNOT_UPDATE = "No se puede actualiza el correo, ya está registrado"
    EMAIL_UNREGISTERED = " Email no registrado."
    USER_ALREADY_REGISTERED = "El Usurio ya esta registrado en el torneo"
    USER_ALREADY_NOT_REGISTERED = "El Usurio no estan inscrito en el torneo"
    USER_CANNOT_TOURNAMENT_ALREADY_STARTED = "El usuario no puede retirarse del torneo, ya empezo"
    USER_NOT_ENROLLMEND_IN_THAT_TOURNAMENT = "Usuario no esta inscrito a ese torneo"
    USER_NOT_REGISTERED_IN_THAT_FOOTBALLGAME = "Usuario no esta registrado para esa jugada"
    USER_MAX_ATTEMPS_VALIDATE_PASSWORD_UPDATE = "Error en la validacion, se supero el maximo de intentos. Vuelve a intentarlo en 30 min."
    USER_FAILED_VALIDATE_PASSWORD_UPDATE = "Error en la recuperacion de la contraseña, los valores ingresados no son los correctos."
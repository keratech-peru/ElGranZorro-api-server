import hashlib
import math
import random
from app.notifications.constants import OTP_DIGIT_LIMIT

def get_hash(string: str) -> str:
    hash_object = hashlib.md5(string.encode("utf-8"))
    return hash_object.hexdigest()

def generate_otp_numeric() -> str:
    digits = "0123456789"
    otp = ""
    cont = 0
    while cont < OTP_DIGIT_LIMIT:
        otp += digits[math.floor(random.random() * 10)]
        cont += 1
    return otp

def popup_message(stage:str) -> str:
    if "ELIMINADO" in stage:
        msg = f"Fuiste eliminado en la etapa de {stage[12:]}, puedes revisar las proximas jugadas"
    elif "GANADOR" in stage:
        msg = "Felicidades ganaste el torneo."
    else:
        msg = ""
    return msg
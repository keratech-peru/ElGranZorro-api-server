class ErrorCode:
    FILE_NOT_ALLOWED = "archivo no permitido."
    TABLE_DOES_NOT_EXIST = "La tabla no existe."
    UNAUTHORIZED = "Usuario no Autorizado."
    FAIL_ACCESS_TOKEN = "Error en el access_token"


RESOURCES = [{"label":"footballgames"}, {"label":"tournaments"}, {"label":"appusers"}]

class ErrorAdmin:
    LOGIN = "Credenciales invalidas"

PAGINATION = {"tournaments" : 10, "footballgames": 23, "appusers": 32}
class Players:
    MAXIMO = "32"
    GAME_MODE = "TORNEO"

class ErrorCode:
    TOURNAMENT_NOT_EXIST = "No existe el torneo"
    FOOTBALLGAME_NOT_EXIST = "No existe footballgame"
    FULL_TOURNAMENT = "Torneo Lleno"
    ALREADY_STARTED_TOURNAMENT = "El Torneo ya empezo."

STATUS_TOURNAMENT = {
    "EE": "EN ESPERA",
    "GP":"GRUPOS",
    "OC":"OCTAVOS",
    "CU":"CUARTOS",
    "SF":"SEMI-FINAL",
    "FI":"FINAL",
    "TE":"TERMINADO"
}

FOOTBALLGAMES_BY_STAGE = {"OC":8, "CU":4, "SF":2, "FI":1}
GROUPS = ["A","B","C","D","E","F","G","H"]

class Origin:
    API = "API-FOOTBALL-DATA"
    HANDBOOK = "MANUAL"
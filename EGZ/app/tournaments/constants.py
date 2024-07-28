class Players:
    MAXIMO = "32"
    GAME_MODE = "TORNEO"

class ErrorCode:
    TOURNAMENT_NOT_EXIST = "No existe el torneo"
    FOOTBALLGAME_NOT_EXIST = "No existe footballgame"
    FULL_TOURNAMENT = "Torneo Lleno"

STATUS_TOURNAMENT = {
    "EE": "EN ESPERA",
    "GP":"GRUPOS",
    "OC":"OCTAVOS",
    "CU":"CUARTOS",
    "SF":"SEMI-FINAL",
    "FI":"FINAL",
    "TE":"TERMINADO"
}

GROUPS = ["A","B","C","D","E","F","G","H"]
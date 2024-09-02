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

FOOTBALLGAMES_BY_STAGE = {"OC":{"number_competencies":8,"days_after_starting":3},
                          "CU":{"number_competencies":4,"days_after_starting":4},
                          "SF":{"number_competencies":2,"days_after_starting":5},
                          "FI":{"number_competencies":1,"days_after_starting":6}}

GROUPS = ["A","B","C","D","E","F","G","H"]
LEVELS = {
    "1":{"quota":20,"reward":320},
    "2":{"quota":50,"reward":800},
    "3":{"quota":80,"reward":1500}
    }

class Origin:
    API = "API-FOOTBALL-DATA"
    HANDBOOK = "MANUAL"
from fastapi import HTTPException, status
from app.tournaments.constants import ErrorCode

tournament_not_exist = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.TOURNAMENT_NOT_EXIST
    },
)

footballgames_not_exist = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.FOOTBALLGAME_NOT_EXIST
    },
)

full_tournament = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.FULL_TOURNAMENT
    },
)

already_started_tournament = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.ALREADY_STARTED_TOURNAMENT
    },
)
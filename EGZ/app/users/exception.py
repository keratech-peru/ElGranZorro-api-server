from fastapi import HTTPException, status
from app.users.constants import ErrorCode

email_already_used = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.EMAIL_ALREADY_USED
    },
)

user_already_registered_tournament = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.USER_ALREADY_REGISTERED
    },
)

user_already_not_registered = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.USER_ALREADY_NOT_REGISTERED
    },
)

user_cannot_withdraw_tournament_already_started = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.USER_CANNOT_TOURNAMENT_ALREADY_STARTED
    },
)

user_not_enrolled_in_tournament = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.USER_NOT_ENROLLMEND_IN_THAT_TOURNAMENT
    },
)

user_not_registered_in_footballgame = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.USER_NOT_REGISTERED_IN_THAT_FOOTBALLGAME
    },
)

email_cannot_updated = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.EMAIL_CANNOT_UPDATE
    },
)
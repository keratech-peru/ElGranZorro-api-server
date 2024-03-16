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

user_not_enrolled_in_tournament = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.USER_NOT_ENROLLMEND_IN_THAT_TOURNAMENT
    },
)
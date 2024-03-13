from fastapi import HTTPException, status
from app.users.constants import ErrorCode

email_already_used = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.EMAIL_ALREADY_USED
    },
)
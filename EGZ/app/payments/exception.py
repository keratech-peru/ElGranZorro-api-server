from fastapi import HTTPException, status
from app.payments.constants import ErrorCode

not_existent_commission_agent = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.NOT_EXISTENT_COMMISSION_AGENT
    },
)

tournament_does_not_exist = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.TOURNAMENT_DOES_NOT_EXIST
    },
)
from fastapi import HTTPException, status
from app.users.constants import ErrorCode

email_already_used = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.EMAIL_ALREADY_USED
    },
)

phone_already_used = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.PHONE_ALREADY_USED
    },
)

user_temporarily_blocked = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.TEMPORARILY_BLOCKED
    },
)

incorrect_otp = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.INCORRECT_OTP
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

phone_cannot_updated = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.PHONE_CANNOT_UPDATE
    },
)

email_unregistered = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.EMAIL_UNREGISTERED
    },
)

user_max_attemps_validate_password_update = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.USER_MAX_ATTEMPS_VALIDATE_PASSWORD_UPDATE
    },
)

user_failed_validate_password_update = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.USER_FAILED_VALIDATE_PASSWORD_UPDATE
    },
)

option_not_allowed = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.OPTION_NOT_ALLOWED
    },
)

user_already_commission_agent= HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.OPTION_NOT_ALLOWED
    },
)

invalid_coupon= HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.INVALID_COUPON
    },
)

coupon_expired= HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.EXPIRED_COUPON
    },
)
from fastapi import HTTPException, status
from app.constants import ErrorCode


api_cms_failure = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.API_CMS_FAILURE
    },
)

invalid_api_lambda_key = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": ErrorCode.INVALID_API_LAMBDA_KEY
    },
)

validate_credentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={"message": ErrorCode.VALIDATE_CREDENTIALS},
    headers={"WWW-Authenticate": "Bearer"},
)

expired_token = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={"message": ErrorCode.EXPIRED_TOKEN},
    headers={"WWW-Authenticate": "Bearer"},
)

user_invalid = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={"message": ErrorCode.USER_INVALID},
    headers={"WWW-Authenticate": "Bearer"},
)
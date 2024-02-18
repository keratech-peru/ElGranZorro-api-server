from fastapi import HTTPException, status
from app.admin.constants import ErrorCode

file_not_allowed = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail={
        "message": ErrorCode.FILE_NOT_ALLOWED
    }
)
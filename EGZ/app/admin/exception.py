from fastapi import HTTPException, status
from app.admin.constants import ErrorCode

file_not_allowed = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail={
        "message": ErrorCode.FILE_NOT_ALLOWED
    }
)

table_does_not_exist = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={
        "message": ErrorCode.TABLE_DOES_NOT_EXIST
    }
)

unauthorized = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail={
        "message": ErrorCode.UNAUTHORIZED
    }
)
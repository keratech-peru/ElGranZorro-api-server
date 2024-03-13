from fastapi import Request, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.exception import invalid_api_lambda_key, api_cms_failure, validate_credentials
from app.config import USERNAME, SECRETE_KEY, TOKEN_SCONDS_EXP
from jose import jwt, JWTError
from app.admin.exception import fail_access_token
from datetime import datetime, timedelta

oauth2_scheme = OAuth2PasswordBearer("/users/login")

def valid_header(request: Request, api_key: str) -> Request:
    flag_aux = request.headers.get("Api-Lambda-Key")
    if flag_aux is None:
        raise api_cms_failure
    if flag_aux == api_key:
        return request
    else:
        raise invalid_api_lambda_key


def valid_access_token(access_token):
    if access_token is None:
        raise fail_access_token
    try:
        data_user = jwt.decode(access_token, key=SECRETE_KEY, algorithms=["HS256"])
        if data_user["username"] != USERNAME:
            raise fail_access_token
    except JWTError:
        raise fail_access_token

def create_token(data: list):
    data_token = data.copy()
    data_token["exp"] = datetime.utcnow() + timedelta(seconds=int(TOKEN_SCONDS_EXP))
    token_jwt = jwt.encode(data_token, key=SECRETE_KEY, algorithm="HS256")
    return token_jwt

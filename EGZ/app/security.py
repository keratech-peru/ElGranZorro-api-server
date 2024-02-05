from fastapi import Request
from app.exception import invalid_api_lambda_key, api_cms_failure


def valid_header(request: Request, api_key: str) -> Request:
    flag_aux = request.headers.get("Api-Lambda-Key")
    if flag_aux is None:
        raise api_cms_failure
    if flag_aux == api_key:
        return request
    else:
        raise invalid_api_lambda_key
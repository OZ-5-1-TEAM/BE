from rest_framework import status
from rest_framework.exceptions import APIException


class DuplicateError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "중복된 데이터가 존재합니다."
    default_code = "duplicate_error"


class InvalidInputError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "잘못된 입력값입니다."
    default_code = "invalid_input"

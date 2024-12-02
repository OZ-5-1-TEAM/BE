from rest_framework import status
from rest_framework.response import Response


class MultipleSerializerMixin:
    """요청 메소드에 따라 다른 시리얼라이저를 사용하는 믹스인"""

    serializer_classes = {}

    def get_serializer_class(self):
        return self.serializer_classes.get(self.request.method, self.serializer_class)

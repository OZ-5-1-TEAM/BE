from rest_framework.response import Response

class CustomResponse:
    @staticmethod
    def success(data=None, message="Success", status=200):
        return Response({
            "status": "success",
            "message": message,
            "data": data
        }, status=status)

    @staticmethod
    def error(message="Error", status=400, errors=None):
        response_data = {
            "status": "error",
            "message": message,
        }
        if errors:
            response_data["errors"] = errors
        return Response(response_data, status=status)
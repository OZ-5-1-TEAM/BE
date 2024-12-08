from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CustomerInquirySerializer

class CustomerInquiryView(APIView):
    def post(self, request):
        serializer = CustomerInquirySerializer(data=request.data)
        if serializer.is_valid():
            inquiry = serializer.save()
            return Response({
                'inquiry_id': inquiry.id,
                'title': inquiry.title,
                'email': inquiry.email,
                'status': inquiry.status,
                'created_at': inquiry.created_at
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'VALIDATION_ERROR',
            'message': '필수 입력값이 누락되었습니다',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
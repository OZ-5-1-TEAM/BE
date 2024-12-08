from django.urls import path
from . import views

app_name = 'customer_services'

urlpatterns = [
    path('inquiries/', views.CustomerInquiryView.as_view(), name='customer-inquiry'),
]

# 고객 문의 생성 (POST /api/v1/customer-service/inquiries)
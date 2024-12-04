from common.permissions import IsOwner
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from common.response import CustomResponse
from .models import Pet
from .serializers import (
    PetCreateSerializer,
    PetDetailSerializer,
    PetListSerializer,
    PetSerializer,
    PetUpdateSerializer,
)


class PetListCreateView(generics.ListCreateAPIView):
    """반려동물 목록 조회 및 생성"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user, is_deleted=False)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PetCreateSerializer
        return PetListSerializer


class PetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """반려동물 상세 조회, 수정, 삭제"""

    permission_classes = [IsAuthenticated, IsOwner]
    lookup_url_kwarg = "pet_id"

    def get_queryset(self):
        return Pet.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PetDetailSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return PetUpdateSerializer
        return PetSerializer

    def perform_destroy(self, instance):
        """소프트 삭제 구현"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

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
    PetImageUploadSerializer,
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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PetImageUploadView(generics.UpdateAPIView):
    """반려동물 이미지 업로드"""
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = PetImageUploadSerializer
    lookup_url_kwarg = "pet_id"

    def get_queryset(self):
        return Pet.objects.filter(is_deleted=False)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(status=status.HTTP_200_OK)


class PetSoftDeleteView(generics.DestroyAPIView):
    """반려동물 소프트 삭제"""
    permission_classes = [IsAuthenticated, IsOwner]
    lookup_url_kwarg = "pet_id"

    def get_queryset(self):
        return Pet.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
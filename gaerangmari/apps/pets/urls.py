from django.urls import path
from . import views

app_name = "pets"

urlpatterns = [
    path("", views.PetListCreateView.as_view(), name="pet-list-create"),
    path("<int:pet_id>/", views.PetDetailView.as_view(), name="pet-detail"),
    path("<int:pet_id>/image/", views.PetImageUploadView.as_view(), name="pet-image-upload"),
    path("<int:pet_id>/soft-delete/", views.PetSoftDeleteView.as_view(), name="pet-soft-delete"),
]

# 반려동물 목록 조회 및 생성 (GET, POST /api/v1/pets)
# 반려동물 상세 조회, 수정, 삭제 (GET, PUT, DELETE /api/v1/pets/{pet_id})
# 반려동물 이미지 업로드 (POST /api/v1/pets/{pet_id}/image)
# 반려동물 소프트 삭제 (POST /api/v1/pets/{pet_id}/soft-delete)
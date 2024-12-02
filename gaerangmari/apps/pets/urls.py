from django.urls import path

from . import views

app_name = "pets"

urlpatterns = [
    path("", views.PetListCreateView.as_view(), name="pet-list-create"),
    path("<int:pet_id>/", views.PetDetailView.as_view(), name="pet-detail"),
]

# 반려동물 목록 조회 및 생성 (GET, POST /api/v1/pets)
# 반려동물 상세 조회, 수정, 삭제 (GET, PUT, DELETE /api/v1/pets/{pet_id})

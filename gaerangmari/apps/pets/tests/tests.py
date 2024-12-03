# tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Pet

User = get_user_model()

class PetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            nickname='Test User'
        )
        self.pet = Pet.objects.create(
            name='멍멍이',
            owner=self.user,
            breed='골든리트리버',
            age=3,
            weight=25.5,
            size='large',
            description='friendly dog'
        )

    def test_pet_creation(self):
        self.assertTrue(isinstance(self.pet, Pet))
        self.assertEqual(str(self.pet), f"{self.user.nickname}의 멍멍이")

    def test_pet_soft_delete(self):
        self.pet.is_deleted = True
        self.pet.save()
        self.assertFalse(Pet.objects.filter(id=self.pet.id, is_deleted=False).exists())

# tests/test_serializers.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from ..models import Pet
from ..serializers import (
    PetSerializer,
    PetListSerializer,
    PetDetailSerializer,
    PetCreateSerializer,
    PetUpdateSerializer
)

User = get_user_model()

class PetSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            nickname='Test User'
        )
        self.pet_data = {
            'name': '멍멍이',
            'breed': '골든리트리버',
            'age': 3,
            'weight': 25.5,
            'size': 'large',
            'description': 'friendly dog'
        }
        self.pet = Pet.objects.create(owner=self.user, **self.pet_data)
        self.factory = APIRequestFactory()

    def test_pet_serializer(self):
        request = self.factory.get('/')
        request.user = self.user
        serializer = PetSerializer(instance=self.pet, context={'request': request})
        data = serializer.data
        
        self.assertEqual(data['name'], self.pet_data['name'])
        self.assertEqual(data['owner_nickname'], self.user.nickname)

    def test_pet_create_serializer_validation(self):
        request = self.factory.get('/')
        request.user = self.user
        
        # Create 4 more pets to reach the limit
        for i in range(4):
            Pet.objects.create(
                name=f'Pet{i}',
                owner=self.user,
                breed='Test breed',
                size='small'
            )
        
        serializer = PetCreateSerializer(
            data=self.pet_data,
            context={'request': request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('반려동물은 최대 5마리까지만 등록할 수 있습니다.', str(serializer.errors))

    def test_pet_update_serializer_validation(self):
        request = self.factory.get('/')
        request.user = self.user
        
        serializer = PetUpdateSerializer(
            data={},
            context={'request': request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('수정할 정보를 입력해주세요.', str(serializer.errors))

# tests/test_views.py
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from ..models import Pet

User = get_user_model()

class PetViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            nickname='Test User'
        )
        self.client.force_authenticate(user=self.user)
        
        self.pet = Pet.objects.create(
            name='멍멍이',
            owner=self.user,
            breed='골든리트리버',
            size='large'
        )
        
        self.list_url = reverse('pet-list')  # Adjust according to your URL configuration
        self.detail_url = reverse('pet-detail', kwargs={'pet_id': self.pet.id})  # Adjust according to your URL configuration

    def test_pet_list_create_view(self):
        # Test GET list
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test POST create
        new_pet_data = {
            'name': '냥냥이',
            'breed': '페르시안',
            'size': 'small',
        }
        response = self.client.post(self.list_url, new_pet_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pet.objects.count(), 2)

    def test_pet_detail_view(self):
        # Test GET detail
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '멍멍이')
        
        # Test PUT update
        update_data = {
            'name': '멍멍이2',
            'breed': '골든리트리버',
            'size': 'large'
        }
        response = self.client.put(self.detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '멍멍이2')
        
        # Test DELETE (soft delete)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Pet.objects.get(id=self.pet.id).is_deleted)

    def test_unauthorized_access(self):
        # Create another user and their pet
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123',
            nickname='Other User'
        )
        other_pet = Pet.objects.create(
            name='다른멍멍이',
            owner=other_user,
            breed='시바견',
            size='medium'
        )
        
        # Try to access other user's pet detail
        other_pet_url = reverse('pet-detail', kwargs={'pet_id': other_pet.id})
        response = self.client.get(other_pet_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
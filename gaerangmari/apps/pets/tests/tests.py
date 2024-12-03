# tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from ..models import Pet

User = get_user_model()

class PetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            nickname='Test User'
        )
        
        self.pet = Pet.objects.create(
            name='멍멍이',
            owner=self.user,
            breed='골든리트리버',
            age=3,
            weight=Decimal('12.5'),
            size='medium',
            description='착한 강아지입니다.'
        )

    def test_pet_creation(self):
        self.assertTrue(isinstance(self.pet, Pet))
        self.assertEqual(str(self.pet), f"{self.user.nickname}의 {self.pet.name}")
        self.assertEqual(self.pet.owner, self.user)
        self.assertEqual(self.pet.breed, '골든리트리버')
        self.assertEqual(self.pet.age, 3)
        self.assertEqual(self.pet.weight, Decimal('12.5'))
        self.assertEqual(self.pet.size, 'medium')
        self.assertEqual(str(self.pet.description), '착한 강아지입니다.')

    def test_pet_image_upload(self):
        image = SimpleUploadedFile(
            "test_pet.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        pet_with_image = Pet.objects.create(
            name='멍멍이',
            owner=self.user,
            breed='골든리트리버',
            image=image
        )
        self.assertTrue(pet_with_image.image.name.startswith('pets/'))

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
class PetViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            nickname='Admin User',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='normal',
            email='normal@test.com',
            password='normal123',
            nickname='Normal User'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            nickname='Test User'
        )
        self.pet = Pet.objects.create(
            name='Test Pet',
            owner=self.user,
            breed='Golden Retriever',
            age=3,
            weight=12.5,
            size='medium',
            description='Test description'
        )

    def test_pet_list_create_view(self):
        url = reverse('pets:pet-list-create')
        
        # 인증되지 않은 접근 테스트
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 인증된 사용자 접근 테스트
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 생성 테스트
        data = {
            'name': 'New Pet',
            'breed': 'Poodle',
            'size': 'small',
            'description': 'New pet description'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_pet_detail_view(self):
        url = reverse('pets:pet-detail', kwargs={'pet_id': self.pet.id})
        
        # 인증되지 않은 접근 테스트
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 소유자가 아닌 사용자 접근 테스트
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 소유자 접근 테스트
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 수정 테스트
        data = {'name': 'Updated Pet Name'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 삭제 테스트
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
# apps/friends/tests/tests.py

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from ..models import FriendRelation

User = get_user_model()

class FriendRelationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass1234',
            nickname='User One',
            email='user1@example.com'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass1234',
            nickname='User Two',
            email='user2@example.com'
        )

    def test_unique_together_constraint(self):
        relation = FriendRelation.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            status='pending'
        )
        self.assertTrue(isinstance(relation, FriendRelation))

class FriendSerializerTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass1234',
            nickname='User One',
            email='user1@example.com'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass1234',
            nickname='User Two',
            email='user2@example.com'
        )

    def test_friend_request_serializer(self):
        relation = FriendRelation.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            status='pending'
        )
        # 시리얼라이저 테스트 로직 추가

class FriendViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass1234',
            nickname='User One',
            email='user1@example.com'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass1234',
            nickname='User Two',
            email='user2@example.com'
        )
        self.client.force_authenticate(user=self.user1)

    def test_friend_list_view(self):
        url = reverse('friends:friend-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_friend_request_create_view(self):
        url = reverse('friends:friend-request-create')
        data = {'to_user': self.user2.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_friend_detail_view(self):
        relation = FriendRelation.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            status='accepted'
        )
        url = reverse('friends:friend-detail', kwargs={'friend_id': relation.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
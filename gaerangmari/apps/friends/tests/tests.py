# tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from ..models import FriendRelation

User = get_user_model()

class FriendRelationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass1234',
            nickname='User One'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass1234',
            nickname='User Two'
        )
        self.friend_relation = FriendRelation.objects.create(
            from_user=self.user1,
            to_user=self.user2
        )

    def test_friend_relation_creation(self):
        self.assertTrue(isinstance(self.friend_relation, FriendRelation))
        self.assertEqual(self.friend_relation.status, 'pending')
        self.assertEqual(
            str(self.friend_relation),
            f"{self.user1.nickname} -> {self.user2.nickname}"
        )

    def test_unique_together_constraint(self):
        with self.assertRaises(IntegrityError):
            FriendRelation.objects.create(
                from_user=self.user1,
                to_user=self.user2
            )

# tests/test_serializers.py
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from ..models import FriendRelation
from ..serializers import (
    FriendRequestSerializer,
    FriendRequestResponseSerializer,
    FriendListSerializer
)

User = get_user_model()

class FriendSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass1234',
            nickname='User One'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass1234',
            nickname='User Two'
        )
        self.friend_request = FriendRelation.objects.create(
            from_user=self.user1,
            to_user=self.user2
        )

    def test_friend_request_serializer(self):
        request = self.factory.post('/')
        request.user = self.user1

        # Test self-request validation
        serializer = FriendRequestSerializer(
            data={'to_user': self.user1.id},
            context={'request': request}
        )
        self.assertFalse(serializer.is_valid())

        # Test duplicate request validation
        serializer = FriendRequestSerializer(
            data={'to_user': self.user2.id},
            context={'request': request}
        )
        self.assertFalse(serializer.is_valid())

    def test_friend_request_response_serializer(self):
        request = self.factory.put('/')
        request.user = self.user2

        serializer = FriendRequestResponseSerializer(
            instance=self.friend_request,
            data={'status': 'accepted'},
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid())

        # Test invalid status
        serializer = FriendRequestResponseSerializer(
            instance=self.friend_request,
            data={'status': 'invalid'},
            context={'request': request}
        )
        self.assertFalse(serializer.is_valid())

# tests/test_views.py
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from ..models import FriendRelation

User = get_user_model()

class FriendViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass1234',
            nickname='User One'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass1234',
            nickname='User Two'
        )
        self.client.force_authenticate(user=self.user1)

    def test_friend_request_create_view(self):
        url = reverse('friend-request-create')
        data = {'to_user': self.user2.id}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            FriendRelation.objects.filter(
                from_user=self.user1,
                to_user=self.user2,
                status='pending'
            ).exists()
        )

    def test_friend_request_response_view(self):
        request = FriendRelation.objects.create(
            from_user=self.user2,
            to_user=self.user1
        )
        url = reverse('friend-request-response', kwargs={'request_id': request.id})
        
        response = self.client.put(url, {'status': 'accepted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        request.refresh_from_db()
        self.assertEqual(request.status, 'accepted')

    def test_friend_list_view(self):
        FriendRelation.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            status='accepted'
        )
        url = reverse('friend-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Test search
        response = self.client.get(f"{url}?search=Two")
        self.assertEqual(len(response.data), 1)
        response = self.client.get(f"{url}?search=NonExistent")
        self.assertEqual(len(response.data), 0)

    def test_friend_detail_view(self):
        relation = FriendRelation.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            status='accepted'
        )
        url = reverse('friend-detail', kwargs={'friend_id': relation.id})
        
        # Test retrieve
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test delete (unfriend)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        relation.refresh_from_db()
        self.assertEqual(relation.status, 'rejected')

    def test_pending_request_list_view(self):
        FriendRelation.objects.create(
            from_user=self.user2,
            to_user=self.user1,
            status='pending'
        )
        url = reverse('pending-requests')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_sent_request_list_view(self):
        FriendRelation.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            status='pending'
        )
        url = reverse('sent-requests')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unauthorized_access(self):
        self.client.logout()
        urls = [
            reverse('friend-request-create'),
            reverse('friend-list'),
            reverse('pending-requests'),
            reverse('sent-requests')
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
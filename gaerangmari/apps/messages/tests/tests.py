# tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import Message

User = get_user_model()

class MessageModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            password='sender123',
            nickname='Sender User'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            password='receiver123',
            nickname='Receiver User'
        )
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Test Message'
        )

    def test_message_creation(self):
        self.assertTrue(isinstance(self.message, Message))
        self.assertEqual(str(self.message), f"From {self.sender.nickname} to {self.receiver.nickname}")
        self.assertFalse(self.message.is_read)
        self.assertIsNone(self.message.read_at)

    def test_soft_delete_by_sender(self):
        self.message.soft_delete(self.sender)
        self.assertTrue(self.message.deleted_by_sender)
        self.assertFalse(self.message.deleted_by_receiver)
        self.assertFalse(self.message.is_deleted)

    def test_soft_delete_by_both(self):
        self.message.soft_delete(self.sender)
        self.message.soft_delete(self.receiver)
        self.assertTrue(self.message.deleted_by_sender)
        self.assertTrue(self.message.deleted_by_receiver)
        self.assertTrue(self.message.is_deleted)
        self.assertIsNotNone(self.message.deleted_at)

# tests/test_serializers.py
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from ..models import Message
from ..serializers import (
    MessageSerializer,
    MessageCreateSerializer,
    MessageListSerializer,
    ReceivedMessageSerializer,
    SentMessageSerializer,
    MessageDeleteSerializer
)

User = get_user_model()

class MessageSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.sender = User.objects.create_user(
            username='sender',
            password='sender123',
            nickname='Sender User'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            password='receiver123',
            nickname='Receiver User'
        )
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Test Message'
        )

    def test_message_serializer(self):
        serializer = MessageSerializer(instance=self.message)
        data = serializer.data
        
        self.assertEqual(data['content'], 'Test Message')
        self.assertEqual(data['sender_nickname'], self.sender.nickname)
        self.assertEqual(data['receiver_nickname'], self.receiver.nickname)

    def test_message_create_serializer_validation(self):
        request = self.factory.post('/')
        request.user = self.sender

        # Test self-messaging validation
        serializer = MessageCreateSerializer(data={
            'receiver': self.sender.id,
            'content': 'Self Message'
        }, context={'request': request})
        self.assertFalse(serializer.is_valid())
        
        # Test content length validation
        serializer = MessageCreateSerializer(data={
            'receiver': self.receiver.id,
            'content': 'a' * 501
        }, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_message_delete_serializer_validation(self):
        request = self.factory.post('/')
        request.user = self.sender
        
        serializer = MessageDeleteSerializer(
            data={'message_ids': [self.message.id]},
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid())

# tests/test_views.py
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from ..models import Message

User = get_user_model()

class MessageViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.sender = User.objects.create_user(
            username='sender',
            password='sender123',
            nickname='Sender User'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            password='receiver123',
            nickname='Receiver User'
        )
        self.client.force_authenticate(user=self.sender)
        
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Test Message'
        )

    def test_message_list_create_view(self):
        url = reverse('message-list-create')  # URL 패턴명 확인 필요
        
        # Test list
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test create
        data = {
            'receiver': self.receiver.id,
            'content': 'New Message'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_received_message_list_view(self):
        self.client.force_authenticate(user=self.receiver)
        url = reverse('received-messages')  # URL 패턴명 확인 필요
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_sent_message_list_view(self):
        url = reverse('sent-messages')  # URL 패턴명 확인 필요
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_message_detail_view(self):
        url = reverse('message-detail', kwargs={'message_id': self.message.id})  # URL 패턴명 확인 필요
        
        # Test retrieve
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Test Message')
        
        # Test delete
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.message.refresh_from_db()
        self.assertTrue(self.message.deleted_by_sender)

    def test_message_read_view(self):
        self.client.force_authenticate(user=self.receiver)
        url = reverse('message-read', kwargs={'message_id': self.message.id})  # URL 패턴명 확인 필요
        
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)
        self.assertIsNotNone(self.message.read_at)

    def test_message_bulk_delete_view(self):
        url = reverse('message-bulk-delete')  # URL 패턴명 확인 필요
        
        response = self.client.post(url, {
            'message_ids': [self.message.id]
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.message.refresh_from_db()
        self.assertTrue(self.message.deleted_by_sender)

    def test_unauthorized_access(self):
        self.client.logout()
        url = reverse('message-list-create')  # URL 패턴명 확인 필요
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
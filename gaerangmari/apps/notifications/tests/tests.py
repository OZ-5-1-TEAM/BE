# tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from ..models import Notification, NotificationTemplate, WebPushSubscription

User = get_user_model()

class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            nickname='Test User'
        )
        self.sender = User.objects.create_user(
            username='sender',
            password='sender123',
            nickname='Sender User'
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            sender=self.sender,
            notification_type='message',
            title='Test Title',
            message='Test Message'
        )

    def test_notification_creation(self):
        self.assertTrue(isinstance(self.notification, Notification))
        self.assertEqual(str(self.notification), f"{self.user.nickname}의 쪽지 알림")
        self.assertFalse(self.notification.is_read)
        self.assertIsNone(self.notification.read_at)

    def test_notification_template_creation(self):
        template = NotificationTemplate.objects.create(
            notification_type='message',
            title_template='{sender}님이 {action}하였습니다',
            message_template='{sender}님이 {content}에 {action}하였습니다'
        )
        self.assertTrue(isinstance(template, NotificationTemplate))
        self.assertEqual(str(template), "쪽지 알림 템플릿")

    def test_web_push_subscription_creation(self):
        subscription = WebPushSubscription.objects.create(
            user=self.user,
            endpoint='https://test.endpoint.com',
            p256dh='test_p256dh_key',
            auth='test_auth_key'
        )
        self.assertTrue(isinstance(subscription, WebPushSubscription))
        self.assertEqual(str(subscription), f"{self.user.nickname}의 웹 푸시 구독")
        self.assertTrue(subscription.is_active)


# tests/test_serializers.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from ..models import Notification, WebPushSubscription
from ..serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationSettingsUpdateSerializer,
    WebPushSubscriptionSerializer
)

User = get_user_model()

class NotificationSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            nickname='Test User'
        )
        self.sender = User.objects.create_user(
            username='sender',
            password='sender123',
            nickname='Sender User'
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            sender=self.sender,
            notification_type='message',
            title='Test Title',
            message='Test Message'
        )

    def test_notification_serializer(self):
        serializer = NotificationSerializer(instance=self.notification)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Test Title')
        self.assertEqual(data['message'], 'Test Message')
        self.assertEqual(data['sender_profile']['nickname'], self.sender.nickname)

    def test_notification_list_serializer(self):
        self.notification.object_id = 1
        self.notification.save()
        
        serializer = NotificationListSerializer(instance=self.notification)
        data = serializer.data
        
        self.assertEqual(data['reference_url'], '/messages/1')

    def test_notification_settings_serializer(self):
        data = {
            'push_enabled': True,
            'message_notification': False
        }
        serializer = NotificationSettingsUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # 빈 데이터 테스트
        serializer = NotificationSettingsUpdateSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_web_push_subscription_serializer(self):
        valid_data = {
            'endpoint': 'https://test.endpoint.com',
            'keys': {
                'p256dh': 'test_p256dh_key',
                'auth': 'test_auth_key'
            }
        }
        serializer = WebPushSubscriptionSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        # 유효하지 않은 데이터 테스트
        invalid_data = {
            'endpoint': 'https://test.endpoint.com',
            'keys': {
                'p256dh': 'test_p256dh_key'
                # auth 키 누락
            }
        }
        serializer = WebPushSubscriptionSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


# tests/test_views.py
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from ..models import Notification, WebPushSubscription

User = get_user_model()

class NotificationViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            nickname='Test User',
            push_enabled=True
        )
        self.client.force_authenticate(user=self.user)
        
        # 테스트용 알림 생성
        self.notifications = []
        for i in range(3):
            self.notifications.append(
                Notification.objects.create(
                    recipient=self.user,
                    notification_type='message',
                    title=f'Test Title {i}',
                    message=f'Test Message {i}'
                )
            )

    def test_notification_list_view(self):
        url = reverse('notification-list')  # URL 패턴명 확인 필요
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # 필터링 테스트
        response = self.client.get(f"{url}?type=message")
        self.assertEqual(len(response.data), 3)
        
        response = self.client.get(f"{url}?type=comment")
        self.assertEqual(len(response.data), 0)

    def test_notification_mark_read_view(self):
        # 단일 알림 읽음 처리 테스트
        url = reverse('notification-mark-read', kwargs={'notification_id': self.notifications[0].id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notifications[0].refresh_from_db()
        self.assertTrue(self.notifications[0].is_read)
        
        # 전체 알림 읽음 처리 테스트
        url = reverse('notification-mark-read')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for notification in self.notifications:
            notification.refresh_from_db()
            self.assertTrue(notification.is_read)

    def test_notification_bulk_delete_view(self):
        url = reverse('notification-bulk-delete')
        
        # 선택 삭제 테스트
        response = self.client.post(url, {
            'notification_ids': [self.notifications[0].id]
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.count(), 2)
        
        # 전체 삭제 테스트
        response = self.client.post(url, {
            'delete_all': True
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.count(), 0)


class WebPushSubscriptionViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            nickname='Test User'
        )
        self.client.force_authenticate(user=self.user)
        
        self.valid_subscription_data = {
            'endpoint': 'https://test.endpoint.com',
            'keys': {
                'p256dh': 'test_p256dh_key',
                'auth': 'test_auth_key'
            }
        }

    def test_web_push_subscription_create(self):
        url = reverse('web-push-subscription')  # URL 패턴명 확인 필요
        response = self.client.post(url, self.valid_subscription_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(WebPushSubscription.objects.filter(user=self.user).exists())

    def test_web_push_subscription_update(self):
        # 먼저 구독 생성
        subscription = WebPushSubscription.objects.create(
            user=self.user,
            endpoint=self.valid_subscription_data['endpoint'],
            p256dh='old_p256dh_key',
            auth='old_auth_key'
        )
        
        # 동일한 endpoint로 업데이트
        url = reverse('web-push-subscription')
        response = self.client.post(url, self.valid_subscription_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subscription.refresh_from_db()
        self.assertEqual(subscription.p256dh, 'test_p256dh_key')
        self.assertEqual(subscription.auth, 'test_auth_key')

    def test_web_push_subscription_delete(self):
        subscription = WebPushSubscription.objects.create(
            user=self.user,
            endpoint=self.valid_subscription_data['endpoint'],
            p256dh='test_p256dh_key',
            auth='test_auth_key'
        )
        
        url = reverse('web-push-subscription')
        response = self.client.delete(url, {
            'endpoint': self.valid_subscription_data['endpoint']
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        subscription.refresh_from_db()
        self.assertFalse(subscription.is_active)
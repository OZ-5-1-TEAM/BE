import os
import sys
from pathlib import Path

# Get the absolute path of the project root
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)

# Add project root to Python path
sys.path.insert(0, PROJECT_ROOT)

# Print paths for debugging
print("Current directory:", os.getcwd())
print("Project root:", PROJECT_ROOT)
print("Python path:", sys.path)

# Set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from users.models import UserProfile
from pets.models import Pet
from posts.models import Post, Comment, Like
from weathers.models import WeatherData, WalkingCondition
from notifications.models import Notification, NotificationTemplate
from direct_messages.models import Message
import random
from datetime import datetime, timedelta

User = get_user_model()

def create_users():
    # Admin 계정
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin1234!',
        nickname='관리자',
        district='강남구',
        neighborhood='역삼동',
        is_staff=True
    )
    UserProfile.objects.create(user=admin, bio='관리자 계정입니다.')

def create_users():
    # Admin 계정
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin1234!',
        nickname='관리자',
        district='강남구',
        neighborhood='역삼동',
        is_staff=True
    )
    UserProfile.objects.create(user=admin, bio='관리자 계정입니다.')

    # 테스트 사용자들
    districts = ['강남구', '서초구', '송파구', '강동구']
    neighborhoods = ['역삼동', '삼성동', '청담동', '대치동']
    
    for i in range(1, 6):
        user = User.objects.create_user(
            username=f'testuser{i}',
            email=f'test{i}@example.com',
            password='test1234!',
            nickname=f'테스트유저{i}',
            district=random.choice(districts),
            neighborhood=random.choice(neighborhoods),
            status='active',
            last_login_at=timezone.now()
        )
        UserProfile.objects.create(
            user=user,
            bio=f'테스트 사용자 {i}의 프로필입니다.'
        )

    # 소셜 로그인 테스트 유저
    social_user = User.objects.create_user(
        username='kakaouser',
        email='kakao@example.com',
        password='social1234!',
        nickname='카카오테스트',
        district='강남구',
        neighborhood='역삼동',
        is_social=True,
        social_provider='kakao',
        social_id='12345'
    )
    UserProfile.objects.create(user=social_user, bio='카카오 소셜 로그인 테스트 계정입니다.')

def create_pets():
    users = User.objects.exclude(is_staff=True)
    breeds = ['골든리트리버', '비숑', '말티즈', '포메라니안', '진돗개']
    sizes = ['small', 'medium', 'large']
    
    for user in users:
        num_pets = random.randint(1, 3)
        for i in range(num_pets):
            Pet.objects.create(
                name=f'{user.nickname}의 반려견{i+1}',
                owner=user,
                breed=random.choice(breeds),
                age=random.randint(1, 10),
                weight=random.uniform(3.0, 25.0),
                size=random.choice(sizes),
                description=f'귀여운 우리 강아지입니다.'
            )

def create_posts():
    users = User.objects.all()
    categories = ['walk', 'care', 'community']
    districts = ['강남구', '서초구', '송파구', '강동구']
    neighborhoods = ['역삼동', '삼성동', '청담동', '대치동']
    
    for _ in range(20):
        author = random.choice(users)
        post = Post.objects.create(
            title=f'테스트 게시글 {_+1}',
            content=f'테스트 게시글의 내용입니다. {_+1}',
            author=author,
            category=random.choice(categories),
            district=random.choice(districts),
            neighborhood=random.choice(neighborhoods),
            dog_size=random.choice(['small', 'medium', 'large']),
            views=random.randint(0, 100)
        )
        
        # 댓글 생성
        for _ in range(random.randint(1, 5)):
            Comment.objects.create(
                post=post,
                author=random.choice(users),
                content=f'테스트 댓글입니다.'
            )
        
        # 좋아요 생성
        for user in random.sample(list(users), random.randint(1, 5)):
            Like.objects.create(post=post, user=user)
            post.likes_count += 1
        post.save()

def create_weather_data():
    districts = ['강남구', '서초구', '송파구', '강동구']
    neighborhoods = ['역삼동', '삼성동', '청담동', '대치동']
    
    current_time = timezone.now()
    
    for district in districts:
        for neighborhood in neighborhoods:
            for hour in range(24):
                forecast_time = current_time + timedelta(hours=hour)
                
                weather = WeatherData.objects.create(
                    district=district,
                    neighborhood=neighborhood,
                    temperature=random.uniform(15.0, 25.0),
                    humidity=random.uniform(40.0, 80.0),
                    wind_speed=random.uniform(0.0, 10.0),
                    precipitation=random.uniform(0.0, 5.0),
                    precipitation_type=random.choice([None, 'rain', 'snow']),
                    walking_score=random.randint(0, 100),
                    forecast_time=forecast_time
                )
                
                WalkingCondition.objects.create(
                    weather_data=weather,
                    recommendation="날씨가 좋아 산책하기 좋은 날입니다." if weather.walking_score > 50 
                    else "실내 활동을 추천드립니다.",
                    warning="비가 예상되니 우산을 챙기세요." if weather.precipitation > 0 else None
                )

def create_notifications_and_messages():
    users = User.objects.all()
    
    # 알림 템플릿 생성
    notification_types = [
        ('message', '새 쪽지가 도착했습니다.'),
        ('friend_request', '새 친구 요청이 있습니다.'),
        ('comment', '게시글에 새 댓글이 달렸습니다.'),
        ('like', '게시글에 좋아요가 달렸습니다.')
    ]
    
    for ntype, title in notification_types:
        NotificationTemplate.objects.create(
            notification_type=ntype,
            title_template=title,
            message_template=f'{title} 확인해보세요.',
            is_active=True
        )
    
    # 알림 생성
    for user in users:
        for _ in range(3):
            Notification.objects.create(
                recipient=user,
                sender=random.choice(users),
                notification_type=random.choice([t[0] for t in notification_types]),
                title='테스트 알림',
                message='테스트 알림 메시지입니다.',
                is_read=random.choice([True, False])
            )
    
    # 쪽지 생성
    for user in users:
        for _ in range(3):
            receiver = random.choice(users)
            if receiver != user:
                Message.objects.create(
                    sender=user,
                    receiver=receiver,
                    content=f'테스트 쪽지입니다. {user.nickname}가 {receiver.nickname}에게 보냅니다.'
                )

def clean_existing_data():
    """기존 데이터를 모두 삭제합니다."""
    print("Cleaning existing data...")
    Message.objects.all().delete()
    Notification.objects.all().delete()
    NotificationTemplate.objects.all().delete()
    Like.objects.all().delete()
    Comment.objects.all().delete()
    Post.objects.all().delete()
    WalkingCondition.objects.all().delete()
    WeatherData.objects.all().delete()
    Pet.objects.all().delete()
    UserProfile.objects.all().delete()
    User.objects.all().delete()

def create_all_dummy_data():
    try:
        # 기존 데이터 삭제
        clean_existing_data()
        
        print("Creating users...")
        create_users()
        
        print("Creating pets...")
        create_pets()
        
        print("Creating posts...")
        create_posts()
        
        print("Creating weather data...")
        create_weather_data()
        
        print("Creating notifications and messages...")
        create_notifications_and_messages()
        
        print("All dummy data created successfully!")
        
    except Exception as e:
        print(f"Error creating dummy data: {e}")

if __name__ == "__main__":
    create_all_dummy_data()
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files import File
from datetime import timedelta
import random
import os
from pathlib import Path
from faker import Faker

from posts.models import Post, Comment, Like, PostImage, Report
from pets.models import Pet
from friends.models import FriendRelation
from direct_messages.models import Message
from notices.models import Notice, NoticeImage, NoticeRead, NoticeFile
from notifications.models import Notification, NotificationTemplate
from customer_services.models import CustomerInquiry

User = get_user_model()
fake = Faker('ko_KR')

class Command(BaseCommand):
    help = 'Generates dummy data for the application'

    def __init__(self):
        super().__init__()
        current_dir = Path(__file__).resolve().parent
        self.dummy_dir = current_dir / 'dummyfile'
        self.dummy_file_path = self.dummy_dir / 'dummy_file.pdf'
        self.dummy_image_path = self.dummy_dir / 'dummy_image.jpg'

    def handle(self, *args, **kwargs):
        # 더미 파일 존재 확인
        if not self.dummy_file_path.exists() or not self.dummy_image_path.exists():
            self.stdout.write(self.style.ERROR('더미 파일이 존재하지 않습니다.'))
            return

        self.stdout.write('Starting dummy data generation...')
        
        # 기존 데이터 삭제
        self.cleanup_existing_data()
        
        # 데이터 생성
        users = self.create_users(20)
        pets = self.create_pets(users)
        posts = self.create_posts(users, 80)
        self.create_comments(users, posts)
        self.create_likes(users, posts)
        self.create_friend_relations(users)
        self.create_messages(users)
        self.create_notices(users)
        self.create_notifications(users)
        self.create_customer_inquiries()
        
        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data'))

    def cleanup_existing_data(self):
        """기존 데이터를 모두 삭제합니다."""
        User.objects.exclude(username='admin').delete()  # admin 계정은 유지
        Post.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
        Pet.objects.all().delete()
        FriendRelation.objects.all().delete()
        Message.objects.all().delete()
        Notice.objects.all().delete()
        Notification.objects.all().delete()
        CustomerInquiry.objects.all().delete()
        self.stdout.write('Cleaned up existing data')

    def get_dummy_pet_image(self):
        return File(open(self.dummy_image_path, 'rb'))

    def get_dummy_additional_image(self):
        additional_images = [
            self.dummy_dir / 'additional1.jpg',
            self.dummy_dir / 'additional2.jpg'
        ]
        return File(open(random.choice(additional_images), 'rb'))

    def get_dummy_profile_image(self):
        profile_images = [
            self.dummy_dir / 'profile1.png',
            self.dummy_dir / 'profile2.png'
        ]
        return File(open(random.choice(profile_images), 'rb'))

    def get_dummy_post_image(self):
        post_image = self.dummy_dir / 'post.png'
        return File(open(post_image, 'rb'))

    def get_dummy_notice_image(self):
        notice_image = self.dummy_dir / 'notice.jpg'
        return File(open(notice_image, 'rb'))

    def get_dummy_image(self):
        return File(open(self.dummy_image_path, 'rb'))

    def get_dummy_file(self):
        return File(open(self.dummy_file_path, 'rb'))
    
    def create_users(self, count):
        users = []
        # 관리자 계정 생성
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            nickname='관리자'
        )
        
        # 관리자 프로필 이미지 설정
        with self.get_dummy_profile_image() as img:
            admin_user.profile_image.save('admin_profile.png', img, save=True)
        users.append(admin_user)

        # 일반 사용자 생성
        districts = ['강남구']
        neighborhoods = ['신사동', '논현동', '역삼동']

        for i in range(count-1):
            username = f'user{i+1}'
            email = f'user{i+1}@example.com'
            nickname = f'{fake.name()[:5]}{i+1}'
            district = random.choice(districts)
            neighborhood = random.choice(neighborhoods)

            self.stdout.write(f"Creating user with nickname: {nickname}")
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                nickname=nickname,
                district=district,
                neighborhood=neighborhood,
                status='active'
            )
            
            # 50% 확률로 프로필 이미지 추가
            if random.random() < 0.5:
                with self.get_dummy_profile_image() as img:
                    user.profile_image.save(f'profile_{i+1}.png', img, save=True)
            users.append(user)

        return users

    def create_pets(self, users):
        pets = []
        breeds = ['말티즈', '푸들', '치와와', '리트리버', '시바견', '진돗개']
        sizes = ['small', 'medium', 'large']

        for user in users:
            num_pets = random.randint(1, 2)
            for j in range(num_pets):
                pet = Pet.objects.create(
                    owner=user,
                    name=fake.first_name(),
                    breed=random.choice(breeds),
                    age=random.randint(1, 10),
                    weight=round(random.uniform(3.0, 25.0), 1),
                    size=random.choice(sizes),
                    description=fake.text(max_nb_chars=200),
                    gender=random.choice(['M', 'F'])
                )
                
                # 메인 이미지 추가
                with self.get_dummy_pet_image() as img:
                    pet.image.save(f'pet_{user.id}_{j+1}.jpg', img, save=True)
                
                # 50% 확률로 추가 이미지 추가
                if random.random() < 0.5:
                    with self.get_dummy_additional_image() as img:
                        pet.additional_image.save(f'pet_{user.id}_{j+1}_additional.jpg', img, save=True)
                
                pets.append(pet)

        return pets

    def create_posts(self, users, count):
        posts = []
        categories = ['notice', 'dog', 'mate']
        districts = ['강남구']
        neighborhoods = ['신사동', '논현동', '역삼동']
        dog_sizes = ['small', 'medium', 'large']

        for i in range(count):
            author = random.choice(users)
            category = random.choice(categories)
            
            post = Post.objects.create(
                title=fake.sentence(),
                content=fake.text(max_nb_chars=500),
                author=author,
                category=category,
                district=random.choice(districts),
                neighborhood=random.choice(neighborhoods),
                dog_size=random.choice(dog_sizes) if category in ['dog', 'mate'] else None,
                views=random.randint(0, 100),
                likes_count=0,
                comments_count=0
            )
            posts.append(post)

            # 게시글 이미지 추가 (1-3장)
            num_images = random.randint(1, 3)
            for j in range(num_images):
                post_image = PostImage(
                    post=post,
                    order=j
                )
                with self.get_dummy_post_image() as img:
                    post_image.image.save(f'post_{post.id}_image_{j+1}.png', img, save=True)

        return posts
        
    def create_notices(self, users):
        admin_users = [user for user in users if user.is_staff]
        if not admin_users:
            return

        for i in range(10):
            notice = Notice.objects.create(
                title=fake.sentence(),
                content=fake.text(),
                author=random.choice(admin_users),
                is_pinned=random.choice([True, False]),
                views=random.randint(0, 100)
            )

            # 공지사항 이미지 추가 (0-2장)
            num_images = random.randint(0, 2)
            for j in range(num_images):
                notice_image = NoticeImage(
                    notice=notice,
                    order=j
                )
                with self.get_dummy_notice_image() as img:
                    notice_image.image.save(f'notice_{notice.id}_image_{j+1}.jpg', img, save=True)

            # 공지사항 첨부파일 추가 (0-2개)
            num_files = random.randint(0, 2)
            for j in range(num_files):
                with self.get_dummy_file() as f:
                    file_size = os.path.getsize(self.dummy_file_path)
                    notice_file = NoticeFile.objects.create(
                        notice=notice,
                        filename=f'공지사항_{notice.id}_첨부파일_{j+1}.pdf',
                        file_size=file_size,
                        download_count=random.randint(0, 50)
                    )
                    notice_file.file.save(f'notice_{notice.id}_file_{j+1}.pdf', f, save=True)

            # 공지사항 읽음 처리
            for user in random.sample(users, random.randint(1, len(users))):
                NoticeRead.objects.create(
                    notice=notice,
                    user=user
                )


    def create_comments(self, users, posts):
        for post in posts:
            num_comments = random.randint(2, 5)
            for _ in range(num_comments):
                parent_comment = Comment.objects.create(
                    post=post,
                    author=random.choice(users),
                    content=fake.text(max_nb_chars=200),
                )

                # 답글 생성 (50% 확률)
                if random.random() < 0.5:
                    Comment.objects.create(
                        post=post,
                        author=random.choice(users),
                        content=fake.text(max_nb_chars=200),
                        parent=parent_comment
                    )

            # 댓글 수 업데이트
            post.comments_count = post.comments.count()
            post.save()

    def create_likes(self, users, posts):
        for post in posts:
            num_likes = random.randint(1, 10)
            random_users = random.sample(users, min(num_likes, len(users)))
            
            for user in random_users:
                Like.objects.create(
                    post=post,
                    user=user
                )
            
            # 좋아요 수 업데이트
            post.likes_count = post.likes.count()
            post.save()

    def create_friend_relations(self, users):
        for user in users:
            num_friends = random.randint(1, 5)
            potential_friends = [u for u in users if u != user]
            random_friends = random.sample(potential_friends, min(num_friends, len(potential_friends)))
            
            for friend in random_friends:
                FriendRelation.objects.create(
                    from_user=user,
                    to_user=friend,
                    status=random.choice(['pending', 'accepted', 'rejected'])
                )

    def create_messages(self, users):
        for _ in range(50):  # 50개의 쪽지 생성
            sender = random.choice(users)
            receiver = random.choice([u for u in users if u != sender])
            
            Message.objects.create(
                sender=sender,
                receiver=receiver,
                content=fake.text(max_nb_chars=200),
                is_read=random.choice([True, False])
            )


    def create_notifications(self, users):
        notification_types = ['message', 'friend_request', 'comment', 'like', 'system']
        
        for _ in range(100):  # 100개의 알림 생성
            recipient = random.choice(users)
            sender = random.choice([u for u in users if u != recipient])
            notification_type = random.choice(notification_types)
            
            Notification.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type=notification_type,
                title=fake.sentence(),
                message=fake.text(max_nb_chars=200),
                is_read=random.choice([True, False])
            )

    def create_customer_inquiries(self):
        districts = ['강남구']
        neighborhoods = ['신사동', '논현동', '역삼동']
        
        for _ in range(30):  # 30개의 고객문의 생성
            CustomerInquiry.objects.create(
                title=fake.sentence(),
                email=fake.email(),
                district=random.choice(districts),
                neighborhood=random.choice(neighborhoods),
                content=fake.text(),
                status=random.choice(['submitted', 'in_progress', 'completed'])
            )
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ..models import Post, Comment, Like, Report, PostImage

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        email='test@example.com',
        password='test1234!',
        nickname='테스트유저',
        district='강남구',
        neighborhood='역삼동'
    )

@pytest.fixture
def admin_user():
    return User.objects.create_user(
        email='admin@example.com',
        password='admin1234!',
        nickname='관리자',
        district='강남구',
        neighborhood='역삼동',
        is_admin=True
    )

@pytest.fixture
def another_user():
    return User.objects.create_user(
        email='another@example.com',
        password='test1234!',
        nickname='다른유저',
        district='강남구',
        neighborhood='역삼동'
    )

@pytest.fixture
def post(user):
    return Post.objects.create(
        title='테스트 게시글',
        content='테스트 내용',
        author=user,
        category='community',
        district='강남구',
        neighborhood='역삼동'
    )

@pytest.fixture
def post_with_image(post):
    image_file = SimpleUploadedFile(
        'test.jpg',
        b'file_content',
        content_type='image/jpeg'
    )
    PostImage.objects.create(
        post=post,
        image=image_file,
        order=0
    )
    return post

@pytest.fixture
def comment(post, user):
    return Comment.objects.create(
        post=post,
        author=user,
        content='테스트 댓글'
    )

@pytest.fixture
def reply(post, user, comment):
    return Comment.objects.create(
        post=post,
        author=user,
        content='테스트 답글',
        parent=comment
    )

@pytest.fixture
def like(post, user):
    return Like.objects.create(post=post, user=user)

@pytest.fixture
def report(post, user):
    return Report.objects.create(
        reporter=user,
        post=post,
        reason='spam',
        description='테스트 신고'
    )
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from ..serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostCreateSerializer,
    CommentSerializer,
    ReportSerializer
)


@pytest.mark.django_db
class TestPostSerializers:
    def test_post_list_serializer(self, post, rf):
        request = rf.get('/')
        serializer = PostListSerializer(post)
        data = serializer.data
        
        assert data['title'] == post.title
        assert data['author_nickname'] == post.author.nickname
        assert 'content' not in data  # list serializer shouldn't include content

    def test_post_detail_serializer(self, post, rf):
        request = rf.get('/')
        request.user = post.author
        serializer = PostDetailSerializer(post, context={'request': request})
        data = serializer.data
        
        assert data['title'] == post.title
        assert data['content'] == post.content
        assert 'author_profile' in data
        assert data['author_profile']['nickname'] == post.author.nickname

    def test_post_create_serializer_with_images(self, user, rf):
        request = rf.post('/')
        request.user = user
        
        image = SimpleUploadedFile(
            'test.jpg',
            b'file_content',
            content_type='image/jpeg'
        )
        
        data = {
            'title': '새 게시글',
            'content': '내용',
            'category': 'community',
            'district': '강남구',
            'neighborhood': '역삼동',
            'images': [image]
        }
        
        serializer = PostCreateSerializer(data=data, context={'request': request})
        assert serializer.is_valid()

    def test_post_create_serializer_image_limit(self, user, rf):
        request = rf.post('/')
        request.user = user
        
        images = [
            SimpleUploadedFile(
                f'test{i}.jpg',
                b'file_content',
                content_type='image/jpeg'
            ) for i in range(6)
        ]
        
        data = {
            'title': '새 게시글',
            'content': '내용',
            'category': 'community',
            'district': '강남구',
            'neighborhood': '역삼동',
            'images': images
        }
        
        serializer = PostCreateSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
        assert 'images' in serializer.errors


@pytest.mark.django_db
class TestCommentSerializer:
    def test_comment_serializer(self, comment):
        serializer = CommentSerializer(comment)
        data = serializer.data
        
        assert data['content'] == comment.content
        assert data['author_nickname'] == comment.author.nickname
        assert 'replies' in data

    def test_comment_with_replies_serializer(self, comment, reply):
        serializer = CommentSerializer(comment)
        data = serializer.data
        
        assert len(data['replies']) == 1
        assert data['replies'][0]['content'] == reply.content
        assert data['replies'][0]['author_nickname'] == reply.author.nickname

    def test_reply_serializer(self, reply):
        serializer = CommentSerializer(reply)
        data = serializer.data
        
        assert data['content'] == reply.content
        assert data['parent'] is not None
        assert len(data['replies']) == 0  # 답글은 replies를 포함하지 않음


@pytest.mark.django_db
class TestReportSerializer:
    def test_post_report_serializer(self, user, post, rf):
        request = rf.post('/')
        request.user = user
        
        data = {
            'post': post.id,
            'reason': 'spam',
            'description': '신고 내용'
        }
        
        serializer = ReportSerializer(data=data, context={'request': request})
        assert serializer.is_valid()

    def test_comment_report_serializer(self, user, comment, rf):
        request = rf.post('/')
        request.user = user
        
        data = {
            'comment': comment.id,
            'reason': 'abuse',
            'description': '신고 내용'
        }
        
        serializer = ReportSerializer(data=data, context={'request': request})
        assert serializer.is_valid()

    def test_invalid_report_serializer(self, user, post, comment, rf):
        request = rf.post('/')
        request.user = user
        
        # 게시글과 댓글을 동시에 지정한 경우
        data = {
            'post': post.id,
            'comment': comment.id,
            'reason': 'spam',
            'description': '신고 내용'
        }
        
        serializer = ReportSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()

    def test_report_without_target_serializer(self, user, rf):
        request = rf.post('/')
        request.user = user
        
        # 게시글이나 댓글을 지정하지 않은 경우
        data = {
            'reason': 'spam',
            'description': '신고 내용'
        }
        
        serializer = ReportSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
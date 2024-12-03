import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Post, Comment, Like, Report

@pytest.mark.django_db
class TestPost:
    def test_create_post(self, user):
        post = Post.objects.create(
            title='테스트 게시글',
            content='테스트 내용',
            author=user,
            category='community',
            district='강남구',
            neighborhood='역삼동'
        )
        assert post.title == '테스트 게시글'
        assert post.author == user
        assert post.views == 0
        assert post.likes_count == 0
        assert post.comments_count == 0
        assert not post.is_deleted

    def test_soft_delete_post(self, post):
        post.is_deleted = True
        post.save()
        assert post.is_deleted
        assert Post.objects.filter(id=post.id).exists()


@pytest.mark.django_db
class TestComment:
    def test_create_comment(self, post, user):
        comment = Comment.objects.create(
            post=post,
            author=user,
            content='테스트 댓글'
        )
        assert comment.content == '테스트 댓글'
        assert comment.author == user
        assert comment.post == post
        assert not comment.is_deleted

    def test_create_reply(self, comment, user):
        reply = Comment.objects.create(
            post=comment.post,
            author=user,
            content='테스트 답글',
            parent=comment
        )
        assert reply.parent == comment
        assert reply.content == '테스트 답글'


@pytest.mark.django_db
class TestLike:
    def test_create_like(self, post, user):
        like = Like.objects.create(post=post, user=user)
        assert like.post == post
        assert like.user == user

    def test_unique_together_constraint(self, post, user, like):
        with pytest.raises(Exception):
            Like.objects.create(post=post, user=user)


@pytest.mark.django_db
class TestReport:
    def test_create_post_report(self, post, user):
        report = Report.objects.create(
            reporter=user,
            post=post,
            reason='spam',
            description='테스트 신고'
        )
        assert report.reporter == user
        assert report.post == post
        assert report.status == 'pending'

    def test_create_comment_report(self, comment, user):
        report = Report.objects.create(
            reporter=user,
            comment=comment,
            reason='abuse',
            description='테스트 신고'
        )
        assert report.reporter == user
        assert report.comment == comment
        assert report.status == 'pending'
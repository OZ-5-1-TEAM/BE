import pytest
from django.urls import reverse
from rest_framework import status
from posts.models import Post, Comment, Report


@pytest.mark.django_db
class TestPostListCreateView:
    def test_list_posts(self, api_client, user, post):
        api_client.force_authenticate(user=user)
        url = reverse('post-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == post.title

    def test_create_post(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('post-list')
        data = {
            'title': '새 게시글',
            'content': '내용',
            'category': 'community',
            'district': '강남구',
            'neighborhood': '역삼동'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(title='새 게시글').exists()

    def test_unauthorized_access(self, api_client):
        url = reverse('post-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPostDetailView:
    def test_retrieve_post(self, api_client, user, post):
        api_client.force_authenticate(user=user)
        url = reverse('post-detail', kwargs={'post_id': post.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == post.title
        assert response.data['content'] == post.content

    def test_update_own_post(self, api_client, user, post):
        api_client.force_authenticate(user=user)
        url = reverse('post-detail', kwargs={'post_id': post.id})
        data = {'title': '수정된 제목'}
        response = api_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert post.title == '수정된 제목'

    def test_update_others_post(self, api_client, another_user, post):
        api_client.force_authenticate(user=another_user)
        url = reverse('post-detail', kwargs={'post_id': post.id})
        data = {'title': '수정된 제목'}
        response = api_client.patch(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_as_admin(self, api_client, admin_user, post):
        api_client.force_authenticate(user=admin_user)
        url = reverse('post-detail', kwargs={'post_id': post.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        post.refresh_from_db()
        assert post.is_deleted


@pytest.mark.django_db
class TestCommentViews:
    def test_create_comment(self, api_client, user, post):
        api_client.force_authenticate(user=user)
        url = reverse('comment-list', kwargs={'post_id': post.id})
        data = {'content': '새 댓글'}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.filter(content='새 댓글').exists()

    def test_create_reply(self, api_client, user, post, comment):
        api_client.force_authenticate(user=user)
        url = reverse('comment-list', kwargs={'post_id': post.id})
        data = {
            'content': '답글',
            'parent': comment.id
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.filter(content='답글', parent=comment).exists()

    def test_delete_comment_as_admin(self, api_client, admin_user, comment):
        api_client.force_authenticate(user=admin_user)
        url = reverse('comment-detail', kwargs={
            'post_id': comment.post.id,
            'comment_id': comment.id
        })
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        comment.refresh_from_db()
        assert comment.is_deleted


@pytest.mark.django_db
class TestLikeView:
    def test_toggle_like(self, api_client, user, post):
        api_client.force_authenticate(user=user)
        url = reverse('post-like', kwargs={'post_id': post.id})
        
        # Create like
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_liked'] is True
        assert post.likes.filter(user=user).exists()
        
        # Remove like
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_liked'] is False
        assert not post.likes.filter(user=user).exists()


@pytest.mark.django_db
class TestReportView:
    def test_create_post_report(self, api_client, user, post):
        api_client.force_authenticate(user=user)
        url = reverse('report')
        data = {
            'post': post.id,
            'reason': 'spam',
            'description': '신고 내용'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Report.objects.filter(post=post, reporter=user).exists()

    def test_create_comment_report(self, api_client, user, comment):
        api_client.force_authenticate(user=user)
        url = reverse('report')
        data = {
            'comment': comment.id,
            'reason': 'abuse',
            'description': '신고 내용'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Report.objects.filter(comment=comment, reporter=user).exists()
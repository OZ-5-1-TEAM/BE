from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Comment, Like, Post, PostImage, Report


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content', 'parent')
        extra_kwargs = {
            'parent': {'required': False, 'allow_null': True}
        }

class PostImageSerializer(serializers.ModelSerializer):
    """게시글 이미지 시리얼라이저"""

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ("id", "image", "image_url", "order")
        extra_kwargs = {"image": {"write_only": True}}

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class CommentSerializer(serializers.ModelSerializer):
    """댓글 시리얼라이저"""

    author_nickname = serializers.CharField(source="author.nickname", read_only=True)
    author_profile = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    level = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "post",
            "author",
            "author_nickname",
            "author_profile",
            "content",
            "parent",
            "replies",
            "created_at",
            "level"
        )
        read_only_fields = ("author", "post", "level")

    def get_author_profile(self, obj):
        return {
            "id": obj.author.id,
            "profile_image": obj.author.profile_image.url
            if obj.author.profile_image
            else None,
        }

    def get_replies(self, obj):
        if obj.parent is None:  # 최상위 댓글인 경우만 답글 포함
            replies = obj.replies.filter(is_deleted=False)
            return CommentSerializer(replies, many=True).data
        return []


class PostListSerializer(serializers.ModelSerializer):
    """게시글 목록 조회용 시리얼라이저"""

    author_nickname = serializers.CharField(source="author.nickname", read_only=True)
    author_profile_image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author_nickname",
            "author_profile_image",
            "category",
            "district",
            "neighborhood",
            "dog_size",
            "thumbnail",
            "likes_count",
            "comments_count",
            "views",
            "created_at",
        )

    def get_author_profile_image(self, obj):
        if obj.author.profile_image:
            return obj.author.profile_image.url
        return None

    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image:
            return first_image.image.url
        return None


class PostDetailSerializer(serializers.ModelSerializer):
    """게시글 상세 조회용 시리얼라이저"""

    author_profile = serializers.SerializerMethodField()
    images = PostImageSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "author_profile",
            "category",
            "district",
            "neighborhood",
            "dog_size",
            "images",
            "comments",
            "likes_count",
            "comments_count",
            "views",
            "is_liked",
            "created_at",
            "updated_at",
        )

    def get_author_profile(self, obj):
        return {
            "id": obj.author.id,
            "nickname": obj.author.nickname,
            "profile_image": obj.author.profile_image.url
            if obj.author.profile_image
            else None,
            "district": obj.author.district,
            "neighborhood": obj.author.neighborhood,
        }

    def get_comments(self, obj):
        # 최상위 댓글만 가져오기 (대댓글은 replies에 포함됨)
        comments = obj.comments.filter(parent=None, is_deleted=False)
        return CommentSerializer(comments, many=True).data

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    """게시글 생성용 시리얼라이저"""

    images = serializers.ListField(
        child=serializers.ImageField(), required=False, write_only=True
    )

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
            "category",
            "district",
            "neighborhood",
            "dog_size",
            "images",
        )

    def validate_images(self, value):
        if len(value) > 5:
            raise serializers.ValidationError(_("이미지는 최대 5개까지만 등록할 수 있습니다."))
        return value

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        validated_data["author"] = self.context["request"].user
        post = super().create(validated_data)

        for index, image in enumerate(images):
            PostImage.objects.create(post=post, image=image, order=index)

        return post


class PostUpdateSerializer(serializers.ModelSerializer):
    """게시글 수정용 시리얼라이저"""

    images = serializers.ListField(
        child=serializers.ImageField(), required=False, write_only=True
    )
    remove_image_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
            "category",
            "district",
            "neighborhood",
            "dog_size",
            "images",
            "remove_image_ids",
        )

    def update(self, instance, validated_data):
        images = validated_data.pop("images", [])
        remove_image_ids = validated_data.pop("remove_image_ids", [])

        # 기존 이미지 삭제
        if remove_image_ids:
            instance.images.filter(id__in=remove_image_ids).delete()

        # 새 이미지 추가
        current_image_count = instance.images.count()
        if current_image_count + len(images) > 5:
            raise serializers.ValidationError(_("이미지는 최대 5개까지만 등록할 수 있습니다."))

        for image in images:
            order = instance.images.count()
            PostImage.objects.create(post=instance, image=image, order=order)

        return super().update(instance, validated_data)


class ReportSerializer(serializers.ModelSerializer):
    """신고 시리얼라이저"""

    reporter_nickname = serializers.CharField(
        source="reporter.nickname", read_only=True
    )

    class Meta:
        model = Report
        fields = (
            "id",
            "reporter",
            "reporter_nickname",
            "post",
            "comment",
            "reason",
            "description",
            "status",
            "created_at",
        )
        read_only_fields = ("reporter", "status")

    def validate(self, data):
        if not data.get("post") and not data.get("comment"):
            raise serializers.ValidationError(_("게시글이나 댓글 중 하나는 지정되어야 합니다."))
        if data.get("post") and data.get("comment"):
            raise serializers.ValidationError(_("게시글과 댓글 중 하나만 지정할 수 있습니다."))
        return data

    def create(self, validated_data):
        validated_data["reporter"] = self.context["request"].user
        return super().create(validated_data)

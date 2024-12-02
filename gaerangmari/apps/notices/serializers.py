from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Notice, NoticeFile, NoticeImage


class NoticeImageSerializer(serializers.ModelSerializer):
    """공지사항 이미지 시리얼라이저"""

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = NoticeImage
        fields = ("id", "image", "image_url", "order")
        extra_kwargs = {"image": {"write_only": True}}

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class NoticeFileSerializer(serializers.ModelSerializer):
    """공지사항 첨부파일 시리얼라이저"""

    class Meta:
        model = NoticeFile
        fields = ("id", "file", "filename", "file_size", "download_count")
        read_only_fields = ("file_size", "download_count")

    def validate_file(self, value):
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError(_("파일 크기는 10MB를 초과할 수 없습니다."))
        return value


class NoticeListSerializer(serializers.ModelSerializer):
    """공지사항 목록 조회용 시리얼라이저"""

    author_nickname = serializers.CharField(source="author.nickname", read_only=True)

    class Meta:
        model = Notice
        fields = ("id", "title", "author_nickname", "is_pinned", "views", "created_at")


class NoticeDetailSerializer(serializers.ModelSerializer):
    """공지사항 상세 조회용 시리얼라이저"""

    author_nickname = serializers.CharField(source="author.nickname", read_only=True)
    images = NoticeImageSerializer(many=True, read_only=True)
    files = NoticeFileSerializer(many=True, read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = (
            "id",
            "title",
            "content",
            "author_nickname",
            "is_pinned",
            "views",
            "images",
            "files",
            "is_read",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
        )

    def get_is_read(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.reads.filter(user=request.user).exists()
        return False


class NoticeCreateSerializer(serializers.ModelSerializer):
    """공지사항 생성용 시리얼라이저"""

    images = serializers.ListField(
        child=serializers.ImageField(), required=False, write_only=True
    )
    files = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True
    )

    class Meta:
        model = Notice
        fields = (
            "title",
            "content",
            "is_pinned",
            "images",
            "files",
            "start_date",
            "end_date",
        )

    def validate_images(self, value):
        if len(value) > 5:
            raise serializers.ValidationError(_("이미지는 최대 5개까지만 등록할 수 있습니다."))
        return value

    def validate_files(self, value):
        if len(value) > 3:
            raise serializers.ValidationError(_("첨부파일은 최대 3개까지만 등록할 수 있습니다."))
        return value

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        files = validated_data.pop("files", [])
        validated_data["author"] = self.context["request"].user
        notice = super().create(validated_data)

        for index, image in enumerate(images):
            NoticeImage.objects.create(notice=notice, image=image, order=index)

        for file_data in files:
            NoticeFile.objects.create(
                notice=notice,
                file=file_data,
                filename=file_data.name,
                file_size=file_data.size,
            )

        return notice


class NoticeUpdateSerializer(serializers.ModelSerializer):
    """공지사항 수정용 시리얼라이저"""

    images = serializers.ListField(
        child=serializers.ImageField(), required=False, write_only=True
    )
    files = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True
    )
    remove_image_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )
    remove_file_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )

    class Meta:
        model = Notice
        fields = (
            "title",
            "content",
            "is_pinned",
            "images",
            "files",
            "start_date",
            "end_date",
            "remove_image_ids",
            "remove_file_ids",
        )

    def update(self, instance, validated_data):
        images = validated_data.pop("images", [])
        files = validated_data.pop("files", [])
        remove_image_ids = validated_data.pop("remove_image_ids", [])
        remove_file_ids = validated_data.pop("remove_file_ids", [])

        # 이미지 삭제 및 추가
        if remove_image_ids:
            instance.images.filter(id__in=remove_image_ids).delete()

        if images:
            current_image_count = instance.images.count()
            if current_image_count + len(images) > 5:
                raise serializers.ValidationError(_("이미지는 최대 5개까지만 등록할 수 있습니다."))

            for image in images:
                order = instance.images.count()
                NoticeImage.objects.create(notice=instance, image=image, order=order)

        # 파일 삭제 및 추가
        if remove_file_ids:
            instance.files.filter(id__in=remove_file_ids).delete()

        if files:
            current_file_count = instance.files.count()
            if current_file_count + len(files) > 3:
                raise serializers.ValidationError(_("첨부파일은 최대 3개까지만 등록할 수 있습니다."))

            for file_data in files:
                NoticeFile.objects.create(
                    notice=instance,
                    file=file_data,
                    filename=file_data.name,
                    file_size=file_data.size,
                )

        return super().update(instance, validated_data)

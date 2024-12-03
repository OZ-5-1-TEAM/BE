# Generated by Django 5.1.3 on 2024-12-03 04:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("title", models.CharField(max_length=200)),
                ("content", models.TextField()),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("notice", "공지사항"),
                            ("walk", "산책"),
                            ("care", "돌봄"),
                            ("community", "자유게시판"),
                        ],
                        max_length=20,
                    ),
                ),
                ("district", models.CharField(max_length=20)),
                ("neighborhood", models.CharField(max_length=20)),
                (
                    "dog_size",
                    models.CharField(
                        blank=True,
                        choices=[("small", "소형"), ("medium", "중형"), ("large", "대형")],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("views", models.PositiveIntegerField(default=0)),
                ("likes_count", models.PositiveIntegerField(default=0)),
                ("comments_count", models.PositiveIntegerField(default=0)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "게시글",
                "verbose_name_plural": "게시글 목록",
            },
        ),
        migrations.CreateModel(
            name="Like",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes",
                        to="posts.post",
                    ),
                ),
            ],
            options={
                "verbose_name": "좋아요",
                "verbose_name_plural": "좋아요 목록",
            },
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("content", models.TextField()),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="replies",
                        to="posts.comment",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="posts.post",
                    ),
                ),
            ],
            options={
                "verbose_name": "댓글",
                "verbose_name_plural": "댓글 목록",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="PostImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("image", models.ImageField(upload_to="posts/%Y/%m/%d/")),
                ("order", models.PositiveSmallIntegerField(default=0)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="posts.post",
                    ),
                ),
            ],
            options={
                "verbose_name": "게시글 이미지",
                "verbose_name_plural": "게시글 이미지 목록",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "reason",
                    models.CharField(
                        choices=[
                            ("spam", "스팸"),
                            ("abuse", "욕설/비방"),
                            ("adult", "성인성 콘텐츠"),
                            ("privacy", "개인정보 노출"),
                            ("etc", "기타"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "대기"),
                            ("accepted", "승인"),
                            ("rejected", "거절"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "comment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reports",
                        to="posts.comment",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reports",
                        to="posts.post",
                    ),
                ),
                (
                    "processed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="processed_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reporter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reports_sent",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "신고",
                "verbose_name_plural": "신고 목록",
            },
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(
                fields=["category", "-created_at"], name="posts_post_categor_bb9705_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(
                fields=["district", "neighborhood"],
                name="posts_post_distric_030b50_idx",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="like",
            unique_together={("post", "user")},
        ),
    ]
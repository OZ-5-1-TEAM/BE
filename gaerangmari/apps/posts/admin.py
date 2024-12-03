from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Post, PostImage, Comment, Like, Report


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'district', 'views', 'likes_count', 'comments_count', 'created_at')
    list_filter = ('category', 'district', 'dog_size')
    search_fields = ('title', 'content', 'author__nickname')
    readonly_fields = ('views', 'likes_count', 'comments_count')
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('post', 'image', 'order')
    raw_id_fields = ('post',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'parent', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__nickname')
    raw_id_fields = ('post', 'author', 'parent')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    raw_id_fields = ('post', 'user')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'post', 'comment', 'reason', 'status', 'created_at')
    list_filter = ('reason', 'status')
    search_fields = ('description', 'reporter__nickname')
    raw_id_fields = ('reporter', 'post', 'comment', 'processed_by')
    readonly_fields = ('processed_at',)
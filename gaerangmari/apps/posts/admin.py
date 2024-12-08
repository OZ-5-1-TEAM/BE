from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Post, PostImage, Comment, Like, Report

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    fields = ['image', 'order']

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ['author', 'content', 'level', 'is_deleted']
    readonly_fields = ['level']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'author_display',
        'category_display',
        'location_display',
        'views',
        'likes_count',
        'comments_count',
        'status_display',
        'created_at'
    ]
    
    list_filter = [
        'category',
        'district',
        'dog_size',
        'is_deleted',
        'created_at'
    ]
    
    search_fields = [
        'title',
        'content',
        'author__nickname',
        'author__email',
        'district',
        'neighborhood'
    ]
    
    readonly_fields = [
        'views',
        'likes_count',
        'comments_count',
        'created_at',
        'updated_at'
    ]
    
    inlines = [PostImageInline, CommentInline]
    
    fieldsets = (
        ('기본 정보', {
            'fields': (
                'title',
                'content',
                'author',
                'category'
            )
        }),
        ('위치 정보', {
            'fields': (
                'district',
                'neighborhood',
                'dog_size'
            )
        }),
        ('통계', {
            'fields': (
                'views',
                'likes_count',
                'comments_count'
            )
        }),
        ('상태 정보', {
            'fields': (
                'is_deleted',
                'deleted_at',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def author_display(self, obj):
        return f"{obj.author.nickname} ({obj.author.email})"
    author_display.short_description = "작성자"
    
    def category_display(self, obj):
        return obj.get_category_display()
    category_display.short_description = "카테고리"
    
    def location_display(self, obj):
        return f"{obj.district} {obj.neighborhood}"
    location_display.short_description = "위치"
    
    def status_display(self, obj):
        if obj.is_deleted:
            return format_html('<span style="color: red;">삭제됨</span>')
        return format_html('<span style="color: green;">게시중</span>')
    status_display.short_description = "상태"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'content_preview',
        'post_title',
        'author_display',
        'level',
        'status_display',
        'created_at'
    ]
    
    list_filter = ['level', 'is_deleted', 'created_at']
    search_fields = ['content', 'author__nickname', 'post__title']
    readonly_fields = ['level', 'created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = "내용"
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = "게시글"
    
    def author_display(self, obj):
        return f"{obj.author.nickname}"
    author_display.short_description = "작성자"
    
    def status_display(self, obj):
        if obj.is_deleted:
            return format_html('<span style="color: red;">삭제됨</span>')
        return format_html('<span style="color: green;">게시중</span>')
    status_display.short_description = "상태"

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'reporter_display',
        'report_target',
        'reason',
        'status',
        'created_at',
        'processed_at'
    ]
    
    list_filter = ['reason', 'status', 'created_at']
    search_fields = [
        'reporter__nickname',
        'description',
        'post__title',
        'comment__content'
    ]
    
    readonly_fields = ['created_at']
    
    def reporter_display(self, obj):
        return f"{obj.reporter.nickname}"
    reporter_display.short_description = "신고자"
    
    def report_target(self, obj):
        if obj.post:
            return f"게시글: {obj.post.title}"
        return f"댓글: {obj.comment.content[:30]}..."
    report_target.short_description = "신고 대상"
    
    actions = ['mark_as_accepted', 'mark_as_rejected']
    
    def mark_as_accepted(self, request, queryset):
        queryset.update(
            status='accepted',
            processed_at=timezone.now(),
            processed_by=request.user
        )
    mark_as_accepted.short_description = "선택된 신고를 승인"
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(
            status='rejected',
            processed_at=timezone.now(),
            processed_by=request.user
        )
    mark_as_rejected.short_description = "선택된 신고를 거절"

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__nickname', 'post__title']
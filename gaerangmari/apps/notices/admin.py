from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Notice, NoticeImage, NoticeFile, NoticeRead

class NoticeImageInline(admin.TabularInline):
    model = NoticeImage
    extra = 1
    fields = ['image', 'order']

class NoticeFileInline(admin.TabularInline):
    model = NoticeFile
    extra = 1
    fields = ['file', 'filename', 'file_size', 'download_count']
    readonly_fields = ['file_size', 'download_count']

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'author_display', 
        'is_pinned', 
        'views', 
        'status_display',
        'created_at'
    ]
    
    list_filter = ['is_pinned', 'is_deleted', 'created_at']
    search_fields = ['title', 'content', 'author__nickname']
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'author', 'is_pinned', 'views')
        }),
        ('게시 기간', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at', 'is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [NoticeImageInline, NoticeFileInline]
    
    def author_display(self, obj):
        return f"{obj.author.nickname}"
    author_display.short_description = "작성자"
    
    def status_display(self, obj):
        now = timezone.now()
        if obj.is_deleted:
            return format_html('<span style="color: red;">삭제됨</span>')
        elif obj.start_date and obj.start_date > now:
            return format_html('<span style="color: orange;">대기중</span>')
        elif obj.end_date and obj.end_date < now:
            return format_html('<span style="color: gray;">종료됨</span>')
        return format_html('<span style="color: green;">게시중</span>')
    status_display.short_description = "상태"

    actions = ['make_deleted', 'make_pinned', 'make_unpinned']
    
    def make_deleted(self, request, queryset):
        queryset.update(is_deleted=True, deleted_at=timezone.now())
    make_deleted.short_description = "선택된 공지사항을 삭제 처리"
    
    def make_pinned(self, request, queryset):
        queryset.update(is_pinned=True)
    make_pinned.short_description = "선택된 공지사항을 상단 고정"
    
    def make_unpinned(self, request, queryset):
        queryset.update(is_pinned=False)
    make_unpinned.short_description = "선택된 공지사항의 상단 고정 해제"

@admin.register(NoticeRead)
class NoticeReadAdmin(admin.ModelAdmin):
    list_display = ['notice', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = [
        'notice__title',
        'user__nickname',
        'user__email'
    ]
    readonly_fields = ['created_at']
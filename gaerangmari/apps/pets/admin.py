from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Pet

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'owner_display',
        'breed',
        'age',
        'weight',
        'gender_display',
        'status_display',
        'created_at'
    ]
    
    list_filter = [
        'gender',
        'breed',
        'size',
        'is_deleted',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'owner__nickname',
        'owner__email',
        'breed',
        'description'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'deleted_at',
        'image_preview'
    ]
    
    fieldsets = (
        ('기본 정보', {
            'fields': (
                'owner',
                'name',
                'breed',
                'gender',
                'age',
                'weight',
                'size'
            )
        }),
        ('추가 정보', {
            'fields': (
                'description',
                'image',
                'image_preview'
            )
        }),
        ('시스템 정보', {
            'fields': (
                'is_deleted',
                'deleted_at',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def owner_display(self, obj):
        return f"{obj.owner.nickname} ({obj.owner.email})"
    owner_display.short_description = "보호자"
    
    def gender_display(self, obj):
        return obj.get_gender_display() if obj.gender else '-'
    gender_display.short_description = "성별"
    
    def status_display(self, obj):
        if obj.is_deleted:
            return format_html('<span style="color: red;">삭제됨</span>')
        return format_html('<span style="color: green;">활성</span>')
    status_display.short_description = "상태"
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px;"/>',
                obj.image.url
            )
        return "이미지 없음"
    image_preview.short_description = "이미지 미리보기"
    
    actions = ['soft_delete', 'restore_pets']
    
    def soft_delete(self, request, queryset):
        queryset.update(
            is_deleted=True,
            deleted_at=timezone.now()
        )
    soft_delete.short_description = "선택된 반려동물을 삭제 처리"
    
    def restore_pets(self, request, queryset):
        queryset.update(
            is_deleted=False,
            deleted_at=None
        )
    restore_pets.short_description = "선택된 반려동물을 복구"
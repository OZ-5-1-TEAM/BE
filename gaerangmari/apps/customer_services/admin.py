from django.contrib import admin
from .models import CustomerInquiry

@admin.register(CustomerInquiry)
class CustomerInquiryAdmin(admin.ModelAdmin):
    # 목록 화면에 표시할 필드들
    list_display = ['title', 'email', 'district', 'neighborhood', 'status', 'created_at', 'updated_at']
    
    # 필터 사이드바에 추가할 필드들
    list_filter = ['status', 'district', 'created_at']
    
    # 검색 가능한 필드들
    search_fields = ['title', 'email', 'content', 'district', 'neighborhood']
    
    # 읽기 전용 필드들
    readonly_fields = ['created_at', 'updated_at']
    
    # 상세 보기 화면에서 필드 그룹화
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'email', 'status')
        }),
        ('위치 정보', {
            'fields': ('district', 'neighborhood')
        }),
        ('문의 내용', {
            'fields': ('content',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # 목록에서 클릭 가능한 필드들
    list_display_links = ['title']
    
    # 목록에서 직접 수정 가능한 필드들
    list_editable = ['status']
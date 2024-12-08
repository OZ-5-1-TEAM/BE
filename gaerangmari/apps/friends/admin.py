from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import FriendRelation

@admin.register(FriendRelation)
class FriendRelationAdmin(admin.ModelAdmin):
    # 목록 화면에 표시할 필드들
    list_display = ['id', 'from_user_display', 'to_user_display', 'status', 'created_at', 'updated_at']
    
    # 필터 기능
    list_filter = ['status', 'created_at']
    
    # 검색 기능
    search_fields = [
        'from_user__nickname', 
        'from_user__email',
        'to_user__nickname', 
        'to_user__email'
    ]
    
    # 읽기 전용 필드
    readonly_fields = ['created_at', 'updated_at']
    
    # 상세 보기 화면 구성
    fieldsets = (
        ('친구 관계 정보', {
            'fields': ('from_user', 'to_user', 'status')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # 목록에서 직접 수정 가능한 필드
    list_editable = ['status']
    
    # 한 페이지당 표시할 항목 수
    list_per_page = 20
    
    def from_user_display(self, obj):
        return f"{obj.from_user.nickname} ({obj.from_user.email})"
    from_user_display.short_description = "요청한 사용자"
    
    def to_user_display(self, obj):
        return f"{obj.to_user.nickname} ({obj.to_user.email})"
    to_user_display.short_description = "요청받은 사용자"
    
    # 액션 추가
    actions = ['make_accepted', 'make_rejected']
    
    def make_accepted(self, request, queryset):
        queryset.update(status='accepted')
    make_accepted.short_description = "선택된 친구 요청을 수락 상태로 변경"
    
    def make_rejected(self, request, queryset):
        queryset.update(status='rejected')
    make_rejected.short_description = "선택된 친구 요청을 거절 상태로 변경"
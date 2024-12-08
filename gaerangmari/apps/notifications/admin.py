from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Notification, NotificationTemplate, WebPushSubscription

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'notification_type_display', 
        'recipient_display', 
        'sender_display', 
        'title', 
        'read_status',
        'delivery_status_display',
        'created_at'
    ]
    
    list_filter = [
        'notification_type', 
        'is_read', 
        'delivery_status',
        'created_at'
    ]
    
    search_fields = [
        'recipient__nickname',
        'recipient__email',
        'sender__nickname',
        'title',
        'message'
    ]
    
    readonly_fields = [
        'created_at', 
        'read_at', 
        'sent_at'
    ]
    
    fieldsets = (
        ('알림 정보', {
            'fields': (
                'notification_type', 
                'recipient', 
                'sender',
                'title', 
                'message'
            )
        }),
        ('상태 정보', {
            'fields': (
                'is_read', 
                'read_at',
                'is_sent',
                'sent_at',
                'delivery_status',
                'error_message'
            )
        }),
        ('연결 정보', {
            'fields': (
                'content_type',
                'object_id'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def notification_type_display(self, obj):
        return obj.get_notification_type_display()
    notification_type_display.short_description = "알림 유형"
    
    def recipient_display(self, obj):
        return f"{obj.recipient.nickname} ({obj.recipient.email})"
    recipient_display.short_description = "수신자"
    
    def sender_display(self, obj):
        if obj.sender:
            return f"{obj.sender.nickname} ({obj.sender.email})"
        return "-"
    sender_display.short_description = "발신자"
    
    def read_status(self, obj):
        if obj.is_read:
            return format_html('<span style="color: green;">읽음</span>')
        return format_html('<span style="color: red;">안읽음</span>')
    read_status.short_description = "읽음 상태"
    
    def delivery_status_display(self, obj):
        colors = {
            'pending': 'orange',
            'sent': 'green',
            'failed': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.delivery_status, 'black'),
            obj.get_delivery_status_display()
        )
    delivery_status_display.short_description = "발송 상태"
    
    actions = ['mark_as_read', 'mark_as_unread', 'resend_notification']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True, read_at=timezone.now())
    mark_as_read.short_description = "선택된 알림을 읽음 처리"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False, read_at=None)
    mark_as_unread.short_description = "선택된 알림을 안읽음 처리"
    
    def resend_notification(self, request, queryset):
        queryset.update(
            delivery_status='pending',
            is_sent=False,
            sent_at=None,
            error_message=None
        )
    resend_notification.short_description = "선택된 알림 재발송"

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'notification_type',
        'title_template',
        'is_active',
        'updated_at'
    ]
    list_filter = ['notification_type', 'is_active']
    search_fields = ['title_template', 'message_template']

@admin.register(WebPushSubscription)
class WebPushSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'endpoint_truncated',
        'is_active',
        'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__nickname', 'user__email', 'endpoint']
    readonly_fields = ['created_at', 'updated_at']
    
    def endpoint_truncated(self, obj):
        return f"{obj.endpoint[:50]}..."
    endpoint_truncated.short_description = "Endpoint"
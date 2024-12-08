from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'short_content', 'is_read', 
                   'created_at', 'deleted_by_sender', 'deleted_by_receiver', 'is_deleted')
    list_filter = ('is_read', 'is_deleted', 'deleted_by_sender', 
                  'deleted_by_receiver', 'created_at', 'read_at')
    search_fields = ('sender__nickname', 'receiver__nickname', 'content')
    readonly_fields = ('created_at', 'read_at', 'deleted_at')
    raw_id_fields = ('sender', 'receiver')
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = '내용'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'receiver')
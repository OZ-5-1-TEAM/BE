from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email', 'nickname', 'is_social', 'social_provider', 
        'status', 'last_login_at', 'is_staff'
    )
    list_filter = (
        'is_social', 'social_provider', 'status', 
        'is_staff', 'is_superuser', 'push_enabled'
    )
    search_fields = ('email', 'nickname', 'district', 'neighborhood')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'nickname', 'profile_image', 'district', 
                'neighborhood', 'status', 'status_reason'
            )
        }),
        (_('Social Login'), {
            'fields': ('is_social', 'social_provider', 'social_id')
        }),
        (_('Notifications'), {
            'fields': (
                'push_enabled', 'message_notification', 
                'friend_notification', 'comment_notification', 
                'like_notification'
            )
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'last_login_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nickname', 'password1', 'password2'),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__nickname', 'bio')
    raw_id_fields = ('user',)
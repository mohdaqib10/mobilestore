from django.contrib import admin

from .models import User, UserToken, UserMobile


class UserModelAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'id', 'name', 'is_active')
    search_fields = ('name', 'email')
    list_filter = ('created_at', 'is_active')


admin.site.register(User, UserModelAdmin)


class UserTokenModelAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'id', 'token', 'expired_at')
    search_fields = ('token',)
    list_filter = ('created_at', 'expired_at')


admin.site.register(UserToken, UserTokenModelAdmin)


class UserMobileModelAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'id', 'user', 'mobile', 'is_primary', 'count')
    search_fields = ('mobile', 'user__name')
    list_filter = ('created_at', 'is_primary')


admin.site.register(UserMobile, UserMobileModelAdmin)

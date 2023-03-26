
from typing import Set
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Video, Comments, User, Profile, FollowersCount, IpModel, WalletUser, Check
from typing import Set
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


admin.site.register(Comments)
admin.site.register(Profile)
admin.site.register(FollowersCount)
admin.site.register(IpModel)
admin.site.register(User)
admin.site.register(WalletUser)
admin.site.register(Check)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()  # type: Set[str]
        if not is_superuser:
            disabled_fields |= {
                'username',
                'is_superuser',
            }
        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True
        return form
        
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'file','author')
    list_display_links = ('id', 'file','author')
    search_fields = ('id','file','author')
    
    
admin.site.register(Video, VideoAdmin)
from django.contrib import admin

from users.models import User, UserAdditionalInfo


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ['username', ]


@admin.register(UserAdditionalInfo)
class UserAdditionalInfoAdmin(admin.ModelAdmin):
    pass

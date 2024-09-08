from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import LibraryUser, MemberProfile


@admin.register(LibraryUser)
class LibraryUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


# admin.site.register(LibraryUser, LibraryUserAdmin)


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_date', 'membership_expiry')
    search_fields = ('user__username', 'user__email')


# admin.site.register(MemberProfile, MemberProfileAdmin)

from django.contrib import admin
from .models import Profile


admin.site.site_header = "Travel-Ease Admin"
admin.site.site_title = "Travel-Ease Admin Portal"
admin.site.index_title = "Welcome to the Travel-Ease Admin Portal"

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_select_related = ('user',)
    search_fields = ('user__username', 'user__email')
    list_filter = ('role',)



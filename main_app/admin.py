from django.contrib import admin
from .models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'state', 'is_seller']  # Add other fields you want to display
    search_fields = ['user__username', 'city', 'state']  # Fields to search by in the admin

admin.site.register(UserProfile, UserProfileAdmin)
# Register your models here.

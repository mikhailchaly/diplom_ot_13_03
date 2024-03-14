from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from new_user.forms import MyUserCreationForm

User = get_user_model()

@admin.register(User)
class UserAdmin(UserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username",  'email', 'type', "password1", "password2")
            },
        ),
    )

    add_form = MyUserCreationForm

    list_display = ['id', 'username', 'email', 'type', 'created_at']
    list_filter = ['created_at']



from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Policy, Conversation

# Register the custom User model with the UserAdmin
admin.site.register(User, UserAdmin)

# Register the Policy model
admin.site.register(Policy)

# Register the Conversation model
admin.site.register(Conversation)
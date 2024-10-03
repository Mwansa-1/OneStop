from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    STATUS_CHOICES = (
        ('staff', 'Staff'),
        ('student', 'Student'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Add related_name to avoid conflict
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',  # Add related_name to avoid conflict
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_input = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user_input} | Bot: {self.bot_response}"

class Policy(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    file = models.FileField(upload_to='files/')
    is_staff_only = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def can_access(self, user):
        if self.is_staff_only and user.status != 'staff':
            return False
        return True
    



    


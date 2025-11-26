from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

from .manager import UserManager

class CustomUser(AbstractUser):
    ROLES = (
        ('parent', 'родитель'),
        ('student', 'ученик'),
        ('child', 'ребенок'),
        ('admin','админ')
    )
    username = None
    email = models.EmailField(unique=True, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)

    telegram_id = models.BigIntegerField(unique=True,null=True, blank=True)
    phone = models.CharField(max_length=13, unique=True, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES, default='student')
    is_active = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=300, blank=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, related_name='children', null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD='email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def create_activation_code(self):
        code = str(uuid.uuid4())
        self.activation_code = code








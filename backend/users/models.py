from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Расширение встроенной модели User."""
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    CHOISES = [
        (USER, 'Аутентифицированный пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    username: str = models.CharField(
        'Username',
        unique=True,
        max_length=150,
    )
    email: str = models.EmailField(
        'E-mail address',
        unique=True,
        blank=False,
        max_length=254,
    )
    role: str = models.CharField(
        max_length=9,
        choices=CHOISES,
        default='user'
    )
    first_name: str = models.CharField(
        'first name',
        max_length=150,
        blank=True
    )
    last_name: str = models.CharField(
        'last name',
        max_length=150,
        blank=True
    )
    date_joined = models.DateTimeField(
        "date joined",
        default=timezone.now
    )
    last_login = models.DateTimeField(
        'last_login',
        blank=True,
        null=True
    )
    location: str = models.CharField(
        'your city',
        max_length=30,
        blank=True
    )
    birth_date = models.DateField(
        'birth_date',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR

    @property
    def is_admin(self):
        return self.role == User.ADMIN

    @property
    def is_user(self):
        return self.role == User.USER

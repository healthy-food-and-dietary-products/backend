from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


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

    def user_directory_path(self, filename):
        '''Строит путь, по которому будет осуществлено сохранение фото пользователя.'''
        return f'images/{self.username}'

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
        default='user',
    )
    location: str = models.CharField(
        'City',
        max_length=30,
        blank=True,
    )
    birth_date = models.DateField(
        'birth_date',
        null=True,
        blank=True,
    )
    address = models.TextField(
        'Address',
        blank=True,
    )
    phone_number = PhoneNumberField(
        'Phone_number',
        blank=True,
    )
    photo = models.ImageField(
        'Photo',
        upload_to=user_directory_path,
        blank=True,
        default='default.jpg',
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

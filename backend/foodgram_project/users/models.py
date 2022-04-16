from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']
    email = models.EmailField(
        verbose_name='Email',
        unique=True
    )

    class Meta:
        ordering = ['date_joined']

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='followers')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow')
        ]

    def __str__(self):
        return f'{self.user} подписался на {self.author}.'

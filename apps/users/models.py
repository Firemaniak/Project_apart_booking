#from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.utils import timezone
from dateutil.relativedelta import relativedelta

from django.db.models.fields import CharField, DecimalField
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.conf import settings

#-----------------------------------------------------------------------------------------------------------------------

def validate_birth_date(value):
    today = timezone.now().date()

    if value > today:
        raise ValidationError('День рождения не может быть в будущем.')

    min_birth_date = today - relativedelta(years=16)
    if value > min_birth_date:
        raise ValidationError('Регистрация возможна только с 16 лет')



class User(AbstractUser):
    #first_name = models.CharField(validators=[MinLengthValidator(3),MaxLengthValidator(10)],
     #                             verbose_name='first name')
    #last_name = models.CharField(validators=[MinLengthValidator(3),MaxLengthValidator(10)],
     #                            verbose_name='last name')
    # is_online = models.BooleanField(default=False)
    nickname = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(
        validators=[validate_birth_date],
        blank=True,
        null=True,
        verbose_name='birth date'
    )
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    address = models.CharField()
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)



    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()



    def __str__(self):
        return f'User: {self.first_name},{self.last_name}' #эти поля должны быть встроены в AbstractUser


    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['nickname',]


    #мягкое удаление
    def delete(self, *args, **kwargs):
        """Мягкое удаление. Запрещаем физическое удаление — только деактивация."""
        self.is_active = False
        self.save()

    def hard_delete(self, *args, **kwargs):
        """На случай, если физическое удаление реально понадобится."""
        super().delete(*args, **kwargs)


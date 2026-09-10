#from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

from django.db.models.fields import CharField, DecimalField
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.conf import settings

#-----------------------------------------------------------------------------------------------------------------------

class User(AbstractUser):
    #first_name = models.CharField(validators=[MinLengthValidator(3),MaxLengthValidator(10)],
     #                             verbose_name='first name')
    #last_name = models.CharField(validators=[MinLengthValidator(3),MaxLengthValidator(10)],
     #                            verbose_name='last name')
    # is_online = models.BooleanField(default=False)
    nickname = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField()
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    address = models.CharField()
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)



    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()



    def __str__(self):
        return f'User: {first_name},{last_name}' #эти поля должны быть встроены в AbstractUser


    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['nickname',]


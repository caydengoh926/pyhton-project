# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):

    mobile = models.CharField(max_length=12, unique=True, verbose_name='phone_number')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    class Meta:
        db_table = 'tb_user'
        verbose_name = 'user'
        verbose_name_plural = verbose_name

    def __str__(self):
        self.username
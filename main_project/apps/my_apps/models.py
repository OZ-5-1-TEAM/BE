from django.db import models

from boilerplate.bases.models import Model
from django.utils.translation import gettext_lazy as _

class MyModel(Model):

    class Meta:
        verbose_name = verbose_name_plural = _('My Model')
        db_table = 'my_model'
        ordering = ['-created']

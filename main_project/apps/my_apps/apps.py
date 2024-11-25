from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MyModelsConfig(AppConfig):
    name = "django_boilerplate.apps.my_mdoel"
    verbose_name = _("My Model")

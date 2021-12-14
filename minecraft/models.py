from django.db import models

from bot_base.models import BaseCogData


class MinecraftCogData(BaseCogData):
    active_profile = models.CharField(max_length=50, default="Vanilla")
    controller_role = models.IntegerField(blank=True, null=True)

from datetime import timedelta

from django.db import models

from bot_base.models import BaseCogData


class ModerationCogData(BaseCogData):
    moderator_role_id = models.IntegerField(blank=True, null=True)
    administrator_role_id = models.IntegerField(blank=True, null=True)
    max_warnings_until_ban = models.IntegerField(default=3)


class ModWarning(models.Model):
    parent_cog = models.ForeignKey(ModerationCogData, on_delete=models.CASCADE, related_name="warnings")
    user_id = models.IntegerField()
    reporter_id = models.IntegerField()
    reason = models.CharField(max_length=100, blank=True, null=True)
    forget_time = models.DurationField(default=timedelta(days=30))
    date_created = models.DateField(auto_now_add=True)

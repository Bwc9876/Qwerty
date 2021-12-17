from django.db import models

from bot_base.models import BaseCogData


class DnDCogData(BaseCogData):
    pass


class Campaign(models.Model):

    parent_cog = models.ForeignKey(DnDCogData, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=100)
    dungeon_master = models.IntegerField()
    date_started = models.DateField(auto_now_add=True)
    date_closed = models.DateField(blank=True, null=True)
    open = models.BooleanField(default=True)


class CampaignSession(models.Model):

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="session")
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    ongoing = models.BooleanField(default=True)


class PartySplit(models.Model):

    session = models.ForeignKey(CampaignSession, on_delete=models.CASCADE, related_name='split')
    root_channel = models.IntegerField()
    channels = models.CharField(max_length=300)


class Player(models.Model):

    parent_campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='players')
    user_id = models.IntegerField()



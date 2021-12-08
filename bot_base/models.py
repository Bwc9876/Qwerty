from django.db import models


class ServerData(models.Model):
    server_id = models.BigIntegerField(primary_key=True)
    prefix = models.CharField(max_length=1, default='~')


class BaseCogData(models.Model):

    CONCRETE = False
    ENABLED_BY_DEFAULT = True

    parent_server = models.ForeignKey(ServerData, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=ENABLED_BY_DEFAULT)

    class Meta:
        abstract = True

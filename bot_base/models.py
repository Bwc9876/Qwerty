from django.db import models


class ServerData(models.Model):
    server_id = models.IntegerField(primary_key=True)


class BaseCogData(models.Model):

    CONCRETE = False
    ENABLED_BY_DEFAULT = True

    parent_server = models.ForeignKey(ServerData, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=ENABLED_BY_DEFAULT)

    class Meta:
        abstract = True

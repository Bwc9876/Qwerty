from django.db import models

from bot_base.cogs import BaseCogData


class MathCogData(BaseCogData):
    pass


class MemoryEntry(models.Model):

    index = models.IntegerField()
    parent_cog = models.ForeignKey(MathCogData, on_delete=models.CASCADE, related_name="mem")
    value = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)

    class Meta:
        unique_together = (
            ('index', 'parent_cog')
        )

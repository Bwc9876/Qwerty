from asgiref.sync import sync_to_async as _
from django.db.models import QuerySet

from bot_base.models import ServerData


async def get_or_create_server_data(server_id: int):
    return (await _(ServerData.objects.get_or_create)(pk=server_id))[0]


async def save_server_data(server_data: ServerData):
    await _(server_data.save)()


async def get_or_create_cog_data(cog_model_class, server_id: int):
    parent_server = await get_or_create_server_data(server_id)
    return (await _(cog_model_class.objects.get_or_create)(parent_server=parent_server))[0]


async def save_cog_data(cog_data):
    await _(cog_data.save)()


def queryset_to_list(queryset: QuerySet):
    return list(queryset)

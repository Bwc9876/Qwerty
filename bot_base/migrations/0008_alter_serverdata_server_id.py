# Generated by Django 4.0 on 2021-12-08 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_base', '0007_alter_serverdata_server_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverdata',
            name='server_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
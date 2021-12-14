# Generated by Django 4.0 on 2021-12-13 16:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('bot_base', '0008_alter_serverdata_server_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='MinecraftCogData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=True)),
                ('active_profile', models.CharField(default='Vanilla', max_length=50)),
                ('controller_role', models.IntegerField(blank=True, null=True)),
                ('parent_server',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot_base.serverdata')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
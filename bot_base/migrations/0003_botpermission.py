# Generated by Django 4.0 on 2021-12-07 22:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot_base', '0002_serverdata_prefix'),
    ]

    operations = [
        migrations.CreateModel(
            name='BotPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100)),
                ('user_id', models.BigIntegerField()),
                ('parent_server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot_base.serverdata')),
            ],
            options={
                'unique_together': {('code', 'user_id', 'parent_server')},
            },
        ),
    ]
# Generated by Django 4.0 on 2021-12-08 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0003_rename_permanentban_ban_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ban',
            name='banner_id',
            field=models.IntegerField(default=1234567890),
            preserve_default=False,
        ),
    ]

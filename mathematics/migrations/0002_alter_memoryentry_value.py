# Generated by Django 4.0 on 2021-12-09 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mathematics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memoryentry',
            name='value',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True),
        ),
    ]

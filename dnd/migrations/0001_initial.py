# Generated by Django 4.0 on 2021-12-17 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bot_base', '0008_alter_serverdata_server_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('dungeon_master', models.IntegerField()),
                ('date_started', models.DateField(auto_now_add=True)),
                ('date_closed', models.DateField(blank=True, null=True)),
                ('open', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CampaignSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('ongoing', models.BooleanField(default=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session', to='dnd.campaign')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('parent_campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='dnd.campaign')),
            ],
        ),
        migrations.CreateModel(
            name='PartySplit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('root_channel', models.IntegerField()),
                ('channels', models.CharField(max_length=300)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='split', to='dnd.campaignsession')),
            ],
        ),
        migrations.CreateModel(
            name='DnDCogData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=True)),
                ('parent_server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot_base.serverdata')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='campaign',
            name='parent_cog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaigns', to='dnd.dndcogdata'),
        ),
    ]
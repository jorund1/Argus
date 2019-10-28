# Generated by Django 2.2.5 on 2019-10-28 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alert', '0003_network_system_network_objects'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='ticket_url',
            field=models.URLField(blank=True, help_text='URL to existing ticket in a ticketing system.', verbose_name='ticket URL'),
        ),
    ]

# Generated by Django 3.2.4 on 2023-02-16 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20230214_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sms_notification',
            field=models.BooleanField(default=False, verbose_name='Уведомление по смс'),
        ),
    ]

# Generated by Django 4.2.11 on 2025-02-03 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
    ]

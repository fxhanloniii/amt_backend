# Generated by Django 5.0 on 2024-01-10 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0008_userprofile_first_name_userprofile_last_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='image_url',
        ),
    ]

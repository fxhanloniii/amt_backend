# Generated by Django 4.2 on 2024-07-13 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0012_favorite'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='zip_code',
            field=models.CharField(blank=True, max_length=12),
        ),
    ]
# Generated by Django 4.2.13 on 2024-06-27 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DMSApp', '0007_lognotifikasi'),
    ]

    operations = [
        migrations.AddField(
            model_name='dokumen',
            name='is_released',
            field=models.BooleanField(default=False, null=True),
        ),
    ]

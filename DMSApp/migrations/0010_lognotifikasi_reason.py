# Generated by Django 5.0.6 on 2024-06-27 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DMSApp', '0009_alter_dokumen_is_approved_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lognotifikasi',
            name='reason',
            field=models.TextField(blank=True),
        ),
    ]

# Generated by Django 4.2.13 on 2024-06-12 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DMSApp', '0003_arsip_is_rejected'),
    ]

    operations = [
        migrations.AddField(
            model_name='arsip',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='arsip',
            name='modified_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]

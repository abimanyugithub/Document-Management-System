# Generated by Django 4.2.13 on 2024-06-25 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DMSApp', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Dokumen',
            new_name='KategoriDokumen',
        ),
        migrations.RenameModel(
            old_name='DokumenLabel',
            new_name='KategoriDokumenLabel',
        ),
    ]

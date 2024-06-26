# Generated by Django 4.2.13 on 2024-06-25 15:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DMSApp', '0003_rename_related_document_departemen_related_category_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Arsip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_no', models.CharField(max_length=100, null=True)),
                ('document_no', models.CharField(max_length=100, null=True)),
                ('sub_document_no', models.CharField(max_length=100, null=True)),
                ('document_name', models.CharField(max_length=100, null=True)),
                ('effective_date', models.DateTimeField(null=True)),
                ('revision_no', models.CharField(max_length=100, null=True)),
                ('revision_date', models.DateTimeField(null=True)),
                ('part_no', models.CharField(max_length=100, null=True)),
                ('part_name', models.CharField(max_length=100, null=True)),
                ('supplier_name', models.CharField(max_length=100, null=True)),
                ('customer_name', models.CharField(max_length=100, null=True)),
                ('is_approved', models.BooleanField(default=False, null=True)),
                ('is_inprogress', models.BooleanField(default=False, null=True)),
                ('is_rejected', models.BooleanField(default=False, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('pdf_file', models.FileField(null=True, upload_to='')),
                ('sheet_file', models.FileField(null=True, upload_to='')),
                ('other_file', models.FileField(null=True, upload_to='')),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True, null=True)),
                ('parent_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DMSApp.kategoridokumen')),
                ('parent_department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DMSApp.departemen')),
            ],
        ),
    ]

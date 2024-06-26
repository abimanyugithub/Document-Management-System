# Generated by Django 4.2.13 on 2024-06-25 13:15

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Departemen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(max_length=100, null=True)),
                ('department_code', models.CharField(blank=True, max_length=10)),
                ('company', models.CharField(blank=True, max_length=100)),
                ('address', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='DokumenLabel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='UserDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_approver', models.BooleanField(default=False)),
                ('is_releaser', models.BooleanField(default=False)),
                ('is_uploader', models.BooleanField(default=False)),
                ('is_ldap', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='DMSApp.departemen')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Dokumen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.CharField(max_length=100, null=True)),
                ('document_initial', models.CharField(max_length=10, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('related_label', models.ManyToManyField(to='DMSApp.dokumenlabel')),
            ],
        ),
        migrations.AddField(
            model_name='departemen',
            name='related_document',
            field=models.ManyToManyField(to='DMSApp.dokumen'),
        ),
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
                ('parent_department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DMSApp.departemen')),
                ('parent_document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DMSApp.dokumen')),
            ],
        ),
    ]

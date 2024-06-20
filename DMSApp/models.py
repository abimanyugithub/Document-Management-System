from django.contrib.auth.models import AbstractUser
from django.db import models
import os
    
# Create your models here.
class Departemen(models.Model):
    department = models.CharField(max_length=100, null=True)
    department_code = models.CharField(max_length=10, null=True, blank=True)
    company = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    related_document = models.ManyToManyField('Dokumen')

    def __str__(self):
        return self.department

class UserDetail(AbstractUser):
    parent_department = models.ForeignKey(Departemen, on_delete=models.CASCADE, null=True)
    is_approver = models.BooleanField(default=False)
    is_releaser = models.BooleanField(default=False)
    is_uploader = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    
class Dokumen(models.Model):
    document = models.CharField(max_length=100, null=True)
    document_initial = models.CharField(max_length=10, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    related_label = models.ManyToManyField('DokumenLabel')

    def __str__(self):
        return self.document

class DokumenLabel(models.Model):
    name = models.CharField(max_length=100)

class Arsip(models.Model):
    parent_document = models.ForeignKey(Dokumen, on_delete=models.CASCADE)
    parent_department = models.ForeignKey(Departemen, on_delete=models.CASCADE)
    form_no = models.CharField(max_length=100, null=True)
    document_no = models.CharField(max_length=100, null=True)
    document_name = models.CharField(max_length=100, null=True)
    effective_date = models.DateTimeField(null=True)
    revision_no = models.CharField(max_length=100, null=True)
    revision_date = models.DateTimeField(null=True)
    part_no = models.CharField(max_length=100, null=True)
    part_name = models.CharField(max_length=100, null=True)
    supplier_name = models.CharField(max_length=100, null=True)
    customer_name = models.CharField(max_length=100, null=True)
    is_approved = models.BooleanField(default=False, null=True)
    is_inprogress = models.BooleanField(default=False, null=True)
    is_rejected = models.BooleanField(default=False, null=True)
    is_active = models.BooleanField(default=True)
    pdf_file = models.FileField(null=True, storage=None) 
    sheet_file = models.FileField(null=True, storage=None)
    other_file = models.FileField(null=True, storage=None)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)

'''class Notifikasi(models.Model):
    dokumen = models.ForeignKey(Dokumen, on_delete=models.CASCADE, null=True)
    lampiran = models.FileField(null=True, storage=None)
    is_active = models.BooleanField(default=True)'''
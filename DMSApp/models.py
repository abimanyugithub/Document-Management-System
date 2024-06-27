from django.contrib.auth.models import AbstractUser
from django.db import models
import os
    
# Create your models here.
class Departemen(models.Model):
    department = models.CharField(max_length=100, null=True)
    department_code = models.CharField(max_length=10, blank=True)
    company = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    related_category = models.ManyToManyField('KategoriDokumen')

    def __str__(self):
        return self.department


class UserDetail(AbstractUser):
    user_department = models.ForeignKey(Departemen, on_delete=models.CASCADE, null=True)
    # ldap_department = models.CharField(max_length=100, null=True)
    is_approver = models.BooleanField(default=False)
    is_releaser = models.BooleanField(default=False)
    is_uploader = models.BooleanField(default=False)
    is_ldap = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    ''' 
    @staticmethod
    def extract_ou_from_dn(dn):
        parts = dn.split(',')
        for part in parts:
            if part.startswith('OU='):
                return part[3:]
        return None

    def save(self, *args, **kwargs):
        if self.distinguishedName:
            department_name = self.extract_ou_from_dn(self.distinguishedName)
            if department_name:
                department, created = Departemen.objects.get_or_create(department=department_name)
                self.parent_department = department
        super(UserDetail, self).save(*args, **kwargs)
    '''

    
class KategoriDokumen(models.Model):
    category = models.CharField(max_length=100, null=True)
    category_initial = models.CharField(max_length=10, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    related_label = models.ManyToManyField('KategoriDokumenLabel')

    def __str__(self):
        return self.category

class KategoriDokumenLabel(models.Model):
    name = models.CharField(max_length=100)

class Dokumen(models.Model):
    parent_category = models.ForeignKey(KategoriDokumen, on_delete=models.CASCADE)
    parent_department = models.ForeignKey(Departemen, on_delete=models.CASCADE)
    form_no = models.CharField(max_length=100, null=True)
    document_no = models.CharField(max_length=100, null=True)
    sub_document_no = models.CharField(max_length=100, null=True)
    document_name = models.CharField(max_length=100, null=True)
    effective_date = models.DateTimeField(null=True)
    revision_no = models.CharField(max_length=100, null=True)
    revision_date = models.DateTimeField(null=True)
    part_no = models.CharField(max_length=100, null=True)
    part_name = models.CharField(max_length=100, null=True)
    supplier_name = models.CharField(max_length=100, null=True)
    customer_name = models.CharField(max_length=100, null=True)
    # status
    is_active = models.BooleanField(default=True)
    is_inprogress = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_released = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    
    pdf_file = models.FileField(null=True, storage=None) 
    sheet_file = models.FileField(null=True, storage=None)
    other_file = models.FileField(null=True, storage=None)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)

'''class Notifikasi(models.Model):
    dokumen = models.ForeignKey(Dokumen, on_delete=models.CASCADE, null=True)
    lampiran = models.FileField(null=True, storage=None)
    is_active = models.BooleanField(default=True)'''

class LogNotifikasi(models.Model):
    time_stamp = models.DateTimeField(auto_now_add=True, null=True)
    parent_user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    parent_document = models.ForeignKey(Dokumen, on_delete=models.CASCADE)
    action = models.CharField(max_length=100, null=True)
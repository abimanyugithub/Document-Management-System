from django.db import models # type: ignore
import os

# Create your models here.
class Departemen(models.Model):
    department = models.CharField(max_length=100, null=True)
    company = models.CharField(max_length=100, null=True)
    location = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    menu_dokumen = models.ManyToManyField('MenuDokumen', blank=True)

    def __str__(self):
        return self.nm_departemen

class MenuDokumen(models.Model):
    document = models.CharField(max_length=100, null=True)
    # dokumen_dept = models.ForeignKey(Departemen, on_delete=models.CASCADE)
    # nm_dokumen = models.CharField(max_length=100, null=True)
    pdf_file = models.BooleanField(default=True)
    sheet_file = models.BooleanField(default=True)
    other_file = models.BooleanField(default=False)
    form_no = models.BooleanField(default=False)
    part_no = models.BooleanField(default=False)
    part_name = models.BooleanField(default=False)
    supplier_name = models.BooleanField(default=False)
    customer_name = models.BooleanField(default=False)
    document_no = models.BooleanField(default=True)
    # default
    document_name = models.BooleanField(default=True)
    effective_date = models.BooleanField(default=True)
    revision_no = models.BooleanField(default=True)
    revision_date = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


class Dokumen(models.Model):
    directory = models.ForeignKey(MenuDokumen, on_delete=models.CASCADE)
    dokumen_dept = models.ForeignKey(Departemen, on_delete=models.CASCADE, null=True)
    no_form = models.CharField(max_length=100, null=True) # no_from
    no_dokumen = models.CharField(max_length=100, null=True) # id_dokumen
    nama_dokumen = models.CharField(max_length=100, null=True) # nm_dokumen
    tanggal_efektif = models.DateTimeField(null=True)
    no_revisi = models.CharField(max_length=100, null=True)
    tanggal_revisi = models.DateTimeField(null=True)
    # file_pdf = models.FileField(null=True, storage=None) 
    # file_sheet = models.FileField(null=True, storage=None)
    no_part = models.CharField(max_length=100, null=True)
    nama_part = models.CharField(max_length=100, null=True)
    nama_supplier = models.CharField(max_length=100, null=True)
    nama_customer = models.CharField(max_length=100, null=True)
    is_approved = models.BooleanField(default=False, null=True)
    is_active = models.BooleanField(default=True)

class LampiranDokumen(models.Model):
    dokumen = models.ForeignKey(Dokumen, on_delete=models.CASCADE, null=True)
    lampiran = models.FileField(null=True, storage=None)
    is_active = models.BooleanField(default=True)

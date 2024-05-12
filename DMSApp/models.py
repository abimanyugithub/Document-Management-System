from django.db import models
import os

# Create your models here.
class Departemen(models.Model):
    nm_departemen = models.CharField(max_length=100, null=True)
    deskripsi = models.CharField(max_length=100, null=True)
    nm_perusahaan = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=True, null=True)

    def __str__(self):
        return self.nm_departemen

class MenuDokumen(models.Model):
    sub_directory = models.CharField(max_length=100, null=True)
    # dokumen_dept = models.ForeignKey(Departemen, on_delete=models.CASCADE)
    # nm_dokumen = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=True, null=True)   

class Dokumen(models.Model):
    directory = models.ForeignKey(MenuDokumen, on_delete=models.CASCADE)
    dokumen_dept = models.ForeignKey(Departemen, on_delete=models.CASCADE, null=True)
    no_dokumen = models.CharField(max_length=100, null=True) # id_dokumen
    nama_dokumen = models.CharField(max_length=100, null=True) # nm_dokumen
    tanggal_efektif = models.DateTimeField(null=True)
    revisi_no = models.CharField(max_length=100, null=True)
    tanggal_revisi = models.DateTimeField(null=True)
    file_pdf = models.FileField(null=True, storage=None) 
    file_sheet = models.FileField(null=True, storage=None)
    is_approved = models.BooleanField(default=False, null=True)
    is_active = models.BooleanField(default=True, null=True)
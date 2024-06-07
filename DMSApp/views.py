from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from .models import Dokumen, Departemen, DokumenLabel, Arsip
from django.conf import settings
from urllib.parse import urljoin
import os
from django import forms
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import PermissionDenied

folder_target = 'media/DMSApp/'
# Create your views here.
class DashboardView(TemplateView):
    template_name = 'DMSApp/Komponen/dashboard.html'


class DepartemenListView(CreateView, ListView):
    model = Departemen
    template_name = 'DMSApp/CrudDepartemen/view.html'
    context_object_name = 'departemen_list'  # For ListView
    fields = ['department_code','department', 'company', 'address']
    success_url = '/departemen/page'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter out objects where is_deleted is False
        #queryset = super().get_queryset().filter(is_deleted=False)
        return queryset.order_by('department')
    
    def form_valid(self, form):
        # Custom form validation
        kode_departemen = form.cleaned_data['department_code']
        nma_departemen = form.cleaned_data['department']
        
        # Check if a department with the same name already exists
        if Departemen.objects.filter(department=nma_departemen).exists() or Departemen.objects.filter(department_code=kode_departemen).exists():
            if Departemen.objects.filter(department=nma_departemen).exists():
                form.add_error('department', "A department with this name already exists.")
            if Departemen.objects.filter(department_code=kode_departemen).exists():
                form.add_error('department_code', "A department with this code already exists.")
            return self.form_invalid(form)
        
        # If validation passes, save the department
        departemen = form.save()
        
        # Handle related documents
        selected_dokumen_ids = self.request.POST.getlist('checklist_dokumen')
        dokumen = Dokumen.objects.filter(id__in=selected_dokumen_ids)
        departemen.related_document.set(dokumen)

        return redirect(self.request.META.get('HTTP_REFERER'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_dokumen'] = Dokumen.objects.filter(is_active=True)
        return context


class DepartemenUpdateView(UpdateView):
    model = Departemen
    fields = []
    
    def post(self, request, pk):
        department_instance_update = Departemen.objects.get(id=pk)
        nma_departemen = request.POST.get('department')
        kode_departemen = request.POST.get('department_code')
        
        # Check if there is an existing Department with the same name, excluding the current department
        departemen_yang_ada = Departemen.objects.filter(department=nma_departemen).exclude(id=pk).exists()
        
        # Check if there is an existing Department with the same code, excluding the current department
        kode_departemen_yang_ada = Departemen.objects.filter(department_code=kode_departemen).exclude(id=pk).exists()

        # Get the current department name
        current_department_name = department_instance_update.department
        
        # If either department name or code already exists, handle errors
        if departemen_yang_ada or kode_departemen_yang_ada:
            # Assuming you have a form instance to pass to the template
            form = self.get_form()
            if departemen_yang_ada:
                form.add_error('department', "A department with this name already exists.")
            if kode_departemen_yang_ada:
                form.add_error('department_code', "A department with this code already exists.")
            return self.form_invalid(form)

        # If no errors, update the department instance
        department_instance_update.department = nma_departemen
        department_instance_update.department_code = kode_departemen
        department_instance_update.save()

        # Handle related documents
        selected_dokumen_ids = request.POST.getlist('checklist_dokumen')
        dokumen = Dokumen.objects.filter(id__in=selected_dokumen_ids)
        department_instance_update.related_document.set(dokumen)
        # department_instance_update.related_document.add(*dokumen)

        # Rename the directory for each selected document
        for dok_id in selected_dokumen_ids:
            try:
                dokumen_instance = Dokumen.objects.get(id=dok_id)
                old_folder_path = os.path.join(folder_target, dokumen_instance.document, current_department_name)
                new_folder_path = os.path.join(folder_target, dokumen_instance.document, nma_departemen)
                
                if os.path.exists(old_folder_path):
                    os.rename(old_folder_path, new_folder_path)
                else:
                    print(f"The directory '{old_folder_path}' does not exist.")
            except Dokumen.DoesNotExist:
                print(f"Dokumen with id {dok_id} does not exist.")

        return redirect(self.request.META.get('HTTP_REFERER'))
    

class DepartemenActivateDeactivateView(UpdateView):

    def post(self, request, pk):
        department_instance_update = Departemen.objects.get(id=pk)
        opsi_aktivasi = request.POST.get('aktivasi')

        if opsi_aktivasi == "nonaktif":
            department_instance_update.is_active = False
            department_instance_update.save(update_fields=['is_active'])
        else:
            department_instance_update.is_active = True
            department_instance_update.save(update_fields=['is_active'])

        return redirect(self.request.META.get('HTTP_REFERER'))
    

class DepartemenDeleteView(DeleteView):

    def post(self, request, pk):
        department_instance_delete = Departemen.objects.get(id=pk)

        # Check if there are related instances of Arsip with the same parent department
        if Arsip.objects.filter(parent_department=pk).exists():
            # If related Arsip instances exist, raise PermissionDenied
            raise PermissionDenied("Cannot delete this department because related Arsip instances exist.")

        # Iterate over each relasi_departemen instance
        for relasi_departemen in department_instance_delete.related_document.all():
            # Construct the path to the directory
            path = os.path.join(folder_target, relasi_departemen.document, department_instance_delete.department)

            if os.path.exists(path):
                os.rmdir(path)

            department_instance_delete.delete()

        return redirect(self.request.META.get('HTTP_REFERER'))
    

# Versi update u/ delete
'''class DepartemenDeleteView(UpdateView):

    def post(self, request, pk):
        department_instance_delete = Departemen.objects.get(id=pk)

        # Check if there are related instances of Arsip with the same parent department
        if Arsip.objects.filter(parent_department=pk).exists():
            # If related Arsip instances exist, raise PermissionDenied
            raise PermissionDenied("Cannot delete this department because related Arsip instances exist.")

        # If no related Arsip instances exist, mark the department as deleted
        department_instance_delete.is_deleted = True
        department_instance_delete.save(update_fields=['is_deleted'])

        return redirect(self.request.META.get('HTTP_REFERER'))'''
    
daftar_label = [{'form_no': {"label": "Form Number", "type": "text"},
                'document_no': {"label": "Document Number", "type": "text"},
                'document_name': {"label": "Document Name", "type": "text"},
                'effective_date': {"label": "Effective Date", "type": "date"},
                'revision_no': {"label": "Revision No", "type": "text"},
                'revision_date': {"label": "Revision Date", "type": "date"},
                'part_no': {"label": "Part Number", "type": "text"},
                'part_name': {"label": "Part Name", "type": "text"},
                'supplier_name': {"label": "Supplier Name", "type": "text"},
                'customer_name': {"label": "Customer Name", "type": "text"},
                'pdf_file': {"label": "PDF File", "type": "file", "extension": ".pdf"},
                'sheet_file': {"label": "Sheet File", "type": "file", "extension": ".ods, .xlsx"},
                'other_file': {"label": "Additional File", "type": "file"}
                }]

class DokumenListView(CreateView, ListView):
    model = Dokumen
    template_name = 'DMSApp/CrudMenuDokumen/view.html'
    context_object_name = 'dokumen_list'  # For ListView
    fields = ['document_initial', 'document']
    success_url = '/document/page/'

    def get_queryset(self):
        return Dokumen.objects.order_by('document')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Specify the fields you want to render as checkboxes dynamically
        context['default_checked'] = ['document_name', 'effective_date', 'revision_no', 'revision_date', 'pdf_file', 'sheet_file']
        context['list_label'] = daftar_label
        return context
    
    def form_valid(self, form):
        # Check if a Dokumen with the same document already exists
        nma_dokumen = form.cleaned_data['document']
        init_dokumen = form.cleaned_data['document_initial']

        # Check for duplicates of document name and document initial
        if Dokumen.objects.filter(document=nma_dokumen).exists() or Dokumen.objects.filter(document_initial=init_dokumen).exists():
            if Dokumen.objects.filter(document=nma_dokumen).exists():
                form.add_error('document', "A document with this name already exists.")
            if Dokumen.objects.filter(document_initial=init_dokumen).exists():
                form.add_error('document_initial', "A document with this initial already exists.")
            return self.form_invalid(form)
        
        # If no duplicates, save the document
        dokumen = form.save()
        
        # Handle related labels
        selected_labels = self.request.POST.getlist('checklist_label')
        for nma_label in selected_labels:
            # Get or create the Label instance
            label, created = DokumenLabel.objects.get_or_create(name=nma_label)
            dokumen.related_label.add(label)
        
        return super().form_valid(form)
            

class DokumenUpdateView(UpdateView):
    model = Dokumen
    fields = []

    def post(self, request, pk):
        document_instance_update = Dokumen.objects.get(id=pk)
        nma_dokumen = request.POST.get('document')
        init_dokumen = request.POST.get('document_initial')
        # Check if there is an existing Dokumen
        dokumen_yang_ada = Dokumen.objects.filter(document=nma_dokumen).exclude(id=pk).exists()

        # Check if there is an existing initial dokumen
        inisial_dokumen_yang_ada = Dokumen.objects.filter(document_initial=init_dokumen).exclude(id=pk).exists()

        # Get the current name of the document
        current_document_name = document_instance_update.document

        # Assuming you have a form instance to pass to the template
        if dokumen_yang_ada or inisial_dokumen_yang_ada:
            form = self.get_form()
            if dokumen_yang_ada:
                form.add_error('department', "A department with this name already exists.")
            if inisial_dokumen_yang_ada:
                form.add_error('inisial_dokumen', "A department with this code already exists.")
            return self.form_invalid(form)
        

        # Otherwise, update the Dokumen instance and redirect
        document_instance_update.document = nma_dokumen
        document_instance_update.document_initial = init_dokumen
        document_instance_update.save()

        # Clear the existing associations
        document_instance_update.related_label.clear()

        # Get the list of selected Label from the request
        selected_labels = request.POST.getlist('checklist_label')
        
        for nma_label in selected_labels:
            # Get or create the Label instance
            label, created = DokumenLabel.objects.get_or_create(name=nma_label)
            document_instance_update.related_label.add(label)

        # Rename the directory
        old_folder_path = os.path.join(folder_target, current_document_name)
        new_folder_path = os.path.join(folder_target, nma_dokumen)
        os.rename(old_folder_path, new_folder_path)

        return redirect(self.request.META.get('HTTP_REFERER'))


class DokumenEnableDisableView(UpdateView):

    def post(self, request, pk):
        menu_document_instance_update = Dokumen.objects.get(id=pk)
        opsi_aktivasi = request.POST.get('aktivasi')

        if opsi_aktivasi == "nonaktif":
            menu_document_instance_update.is_active = False
            menu_document_instance_update.save(update_fields=['is_active'])
        else:
            menu_document_instance_update.is_active = True
            menu_document_instance_update.save(update_fields=['is_active'])

        return redirect(self.request.META.get('HTTP_REFERER'))
    

class MenuDokumenListView(ListView):
    model = Departemen
    template_name = 'DMSApp/CrudArsip/view.html'
    context_object_name = 'departemen_list'

    def get_queryset(self):
        # Get the nama_dept from the request parameters
        nma_departemen = self.request.GET.get('dept')

        if nma_departemen:
            # Retrieve the Departemen object with the given department_id
            departemen = Departemen.objects.get(department=nma_departemen)
                
            # Retrieve the related MenuDokumen objects for the Departemen
            queryset = departemen.related_document.all().order_by('document')
        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nma_dokumen = self.request.GET.get('menu')
        nma_departemen = self.request.GET.get('dept')

        if nma_departemen:
            context['nm_departemen'] = nma_departemen
            if nma_dokumen:
                context['nm_dokumen'] = nma_dokumen
                context['data_dokumen_list'] = Dokumen.objects.filter(document=nma_dokumen)
                nma_label = Dokumen.objects.get(document=nma_dokumen)
                relasi_label = nma_label.related_label.all()
                context['nm_label'] = relasi_label
                context['list_label'] = daftar_label
                context['arsip_list'] = Arsip.objects.all()
            
        return context
    

# contoh penomoran dokumen => 2. FMS.31.01 REV.02_MEMBUAT TAGIHAN CUSTOMER 8. FMS.31.05.02 REV.02_PPH 21 
class ArchiveCreateView(CreateView):
    model = Arsip
    template_name = 'DMSApp/CrudArsip/create.html'
    fields = []  # Remove fields, as we are handling them manually

    def form_valid(self, form):
        # Get the values of menu1 and dept1 from the form
        nm_dokumen = self.request.POST.get('dokumen')
        nm_departemen = self.request.POST.get('departemen')
        
        # Retrieve IDs from the database based on the names
        dokumen_obj = Dokumen.objects.get(document=nm_dokumen)  
        departemen_obj = Departemen.objects.get(department=nm_departemen)  
        
        # Set the IDs to the form instance before saving
        form.instance.parent_document = dokumen_obj
        form.instance.parent_department = departemen_obj

        # Save the form
        self.object = form.save()

        # Handle saving dynamic fields and files
        directory = os.path.join(folder_target, nm_dokumen, nm_departemen)
        
        # Ensure the directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save dynamic form fields
        for label_dict in daftar_label:
            for key, value in label_dict.items():

                # Check if the field is a file input
                if value.get('type') == "file":

                    # Handle file upload
                    file_value = self.request.FILES.get(key)
                    if file_value:
                        fs = FileSystemStorage(location=directory)
                        filename = fs.save(file_value.name, file_value)

                        # Set the file path to the form instance dynamically
                        # setattr(self.object, key, os.path.join(directory, filename))
                        setattr(self.object, key, filename)
                        
                else:

                    # Get the value of the field from the request
                    field_value = self.request.POST.get(key)
                    setattr(self.object, key, field_value)
        
        # Now save the instance to the database
        self.object.save()

        return redirect(self.request.META.get('HTTP_REFERER'))
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nma_dokumen = self.request.GET.get('menu')
        nma_departemen = self.request.GET.get('dept')
        if nma_dokumen:
            # Retrieve the related MenuDokumen objects for the Departemen
            nma_label = Dokumen.objects.get(document=nma_dokumen)
            relasi_label = nma_label.related_label.all()
            context['nm_dokumen'] = nma_dokumen
            context['nm_departemen'] = nma_departemen
            context['nm_label'] = relasi_label
            context['list_label'] = daftar_label
        return context
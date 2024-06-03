from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from .models import Dokumen, Departemen, DokumenLabel, Arsip
from django.conf import settings
from urllib.parse import urljoin
import os
from django import forms

folder_target = 'media/DMSApp/'
# Create your views here.
class DashboardView(TemplateView):
    template_name = 'DMSApp/Komponen/dashboard.html'


class DepartemenListView(CreateView, ListView):
    model = Departemen
    template_name = 'DMSApp/CrudDepartemen/view.html'
    context_object_name = 'departemen_list'  # For ListView
    fields = ['department', 'company', 'address']
    success_url = '/departemen/page'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('department')
    
    def form_valid(self, form):
        # Custom form validation
        nma_departemen = form.cleaned_data['department']
        if Departemen.objects.filter(department=nma_departemen).exists():
            form.add_error('department', "A department with this name already exists.")
            return self.form_invalid(form)
        else:
            departemen = form.save()
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
    fields = ['department', 'company', 'address']
    
    def post(self, request, pk):
        department_instance_update = Departemen.objects.get(id=pk)
        nma_departemen = request.POST.get('department')
        # Check if there is an existing Department
        departemen_yang_ada = Departemen.objects.filter(department=nma_departemen).exclude(id=pk).exists()
        
        if not departemen_yang_ada:
            # Update other fields if there's no existing Department instance with the same values
            for field in self.fields:
                if request.POST.get(field):
                    setattr(department_instance_update, field, request.POST.get(field))

            # Save the updated fields
            department_instance_update.save(update_fields=self.fields)

            # Clear the existing associations
            department_instance_update.related_document.clear()

            # Get the list of selected Dokumen ids from the request
            selected_dokumen_ids = request.POST.getlist('checklist_dokumen')

            # Associate the selected Dokumen instances with the Departemen
            selected_dokumen = Dokumen.objects.filter(id__in=selected_dokumen_ids)
            # "*" operator is used to unpack the selected_dokumen iterable, which contains instances that need to be added to the related_documents field
            department_instance_update.related_document.add(*selected_dokumen)

        return redirect(self.request.META.get('HTTP_REFERER'))
    

class DepartemenEnableDisableView(UpdateView):

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
    

'''def add_menu(request):
    if request.method == 'POST':
        new_menu_name = request.POST.get('new_menu')
        add_additional = request.POST.get('additional') == 'on'  # Check if the checkbox is checked
        if new_menu_name:
            if not MenuDokumen.objects.filter(document=new_menu_name).exists():
                MenuDokumen.objects.create(document=new_menu_name, is_additional=add_additional)
                # Define the directory path
                directory = folder_target + new_menu_name
                # Create the directory if it doesn't exist
                if not os.path.exists(directory):
                    os.makedirs(directory)
                # return JsonResponse({'success': True, 'menu_name': menu.name})
            
    return redirect(request.META.get('HTTP_REFERER'))
'''

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
    fields = ['document']
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
        if Dokumen.objects.filter(document=nma_dokumen).exists():
            return self.form_invalid(form)
        else:
            dokumen = form.save()
            selected_labels = self.request.POST.getlist('checklist_label')
            for nma_label in selected_labels:
                # Get or create the Label instance
                label, created = DokumenLabel.objects.get_or_create(name=nma_label)
                dokumen.related_label.add(label)
            return super().form_valid(form)
            

class DokumenUpdateView(UpdateView):
    model = Dokumen
    fields = ['document']

    def post(self, request, pk):
        document_instance_update = Dokumen.objects.get(id=pk)
        nma_dokumen = request.POST.get('document')
        # Check if there is an existing Dokumen
        dokumen_yang_ada = Dokumen.objects.filter(document=nma_dokumen).exclude(id=pk).exists()
        
        if not dokumen_yang_ada:
            # Update other fields if there's no existing Dokumen instance with the same values
            for field in self.fields:
                if request.POST.get(field):
                    setattr(document_instance_update, field, request.POST.get(field))

            # Save the updated fields
            document_instance_update.save(update_fields=self.fields)

            # Clear the existing associations
            document_instance_update.related_label.clear()

            # Get the list of selected Label from the request
            selected_labels = request.POST.getlist('checklist_label')
            
            for nma_label in selected_labels:
                # Get or create the Label instance
                label, created = DokumenLabel.objects.get_or_create(name=nma_label)
                document_instance_update.related_label.add(label)

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
            # nm_directory = MenuDokumen.objects.get(sub_directory=menu_name)
            context['nm_dokumen'] = nma_dokumen
            context['nm_departemen'] = nma_departemen
            # context['menu_dokumen_list'] = Dokumen.objects.filter(document=nma_dokumen)
        return context

class ArchiveCreateView(CreateView):
    model = Arsip
    template_name = 'DMSApp/CrudArsip/create.html'
    fields = ['parent_document', 'parent_department']
    success_url = '/document/page'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nma_dokumen = self.request.GET.get('menu')
        nma_departemen = self.request.GET.get('dept')
        if nma_dokumen:
            # Retrieve the related MenuDokumen objects for the Departemen
            nma_label = Dokumen.objects.get(document=nma_dokumen)
            context['nm_dokumen'] = nma_dokumen
            context['nm_department'] = nma_departemen
            context['nm_label'] = nma_label.related_label.all()
            context['list_label'] = daftar_label
        return context

'''
    def get_queryset(self):
        queryset = super().get_queryset()
        nama_dept = self.request.GET.get('dept')
        if nama_dept:
            queryset = queryset.filter(menu_dokumen__departemen__department=nama_dept).distinct()
        return queryset
    
    def get_queryset(self):
        nama_dept = self.request.GET.get('dept')
        # queryset = queryset.filter(menu_dokumen__departemen__department=nama_dept)
        queryset = Departemen.objects.get(menu_dokumen__departemen__department=nama_dept)
        # departemen = Departemen.objects.get(pk=departemen_id)
        return queryset
        '''
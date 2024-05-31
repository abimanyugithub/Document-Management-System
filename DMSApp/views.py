from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from .models import MenuDokumen, Departemen, Dokumen, LampiranDokumen
from django.shortcuts import redirect
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
    fields = ['department', 'company', 'location']
    success_url = '/departemen/page'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('department')
    
    def form_valid(self, form):
        # Custom form validation
        nm_departemen = form.cleaned_data['department']
        if Departemen.objects.filter(department=nm_departemen).exists():
            form.add_error('department', "A department with this name already exists.")
            return self.form_invalid(form)
        else:
            departemen = form.save()
            menu_dokumen_ids = self.request.POST.getlist('ceklis_dokumen')
            menu_dokumen = MenuDokumen.objects.filter(id__in=menu_dokumen_ids)
            departemen.menu_dokumen.set(menu_dokumen)

        return redirect(self.request.META.get('HTTP_REFERER'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_menu_dokumen'] = MenuDokumen.objects.all()
        return context

class DepartemenUpdateView(UpdateView):
    model = Departemen
    fields = ['department', 'company', 'location']
    
    def post(self, request, pk):
        department_instance_update = Departemen.objects.get(id=pk)
        nama_dept = request.POST.get('department')
        # Check if there is an existing Department instance with the same no_dokumen and nama_dokumen
        existing_department = Departemen.objects.filter(department=nama_dept).exclude(id=pk).exists()
        
        if not existing_department:
            # Update other fields if there's no existing Department instance with the same values
            for field in self.fields:
                if request.POST.get(field):
                    setattr(department_instance_update, field, request.POST.get(field))

            # Save the updated fields
            department_instance_update.save(update_fields=self.fields)
            # Get the list of selected MenuDokumen ids from the request
            selected_menu_dokumen_ids = request.POST.getlist('ceklis_dokumen')

            # Clear the existing associations
            department_instance_update.menu_dokumen.clear()

            # Associate the selected MenuDokumen instances with the Departemen
            selected_menu_dokumen = MenuDokumen.objects.filter(id__in=selected_menu_dokumen_ids)
            # "*" operator is used to unpack the selected_menu_dokumen iterable, which contains instances that need to be added to the menu_dokumen field
            department_instance_update.menu_dokumen.add(*selected_menu_dokumen)

        return redirect(self.request.META.get('HTTP_REFERER'))
    

class DepartemenEnableDisableView(UpdateView):

    def post(self, request, pk):
        department_instance_update = Departemen.objects.get(id=pk)
        set_aktif = request.POST.get('aktivasi')

        if set_aktif == "nonaktif":
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
            
    return redirect(request.META.get('HTTP_REFERER'))'''

class MenuDokumenListView(CreateView, ListView):
    model = MenuDokumen
    template_name = 'DMSApp/CrudMenuDokumen/view.html'
    context_object_name = 'menu_dokumen_list'  # For ListView
    fields = ['document', 'form_no', 'document_no', 'document_name',
              'effective_date', 'revision_no', 'revision_date', 'part_no', 'part_name','supplier_name',
              'customer_name', 'pdf_file', 'sheet_file', 'other_file']
    success_url = '/menu-dokumen/page/'

    def get_queryset(self):
        return MenuDokumen.objects.order_by('document')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Specify the fields you want to render as checkboxes dynamically
        context['default_checked'] = ['document', 'effective_date', 'revision_no', 'revision_date', 'pdf_file', 'sheet_file']
        # context['doc_file'] = ['doc_pdf', 'doc_sheet', 'doc_additional']
        return context
    
class MenuDokumenUpdateView(UpdateView):
    model = MenuDokumen
    fields = ['document', 'form_no', 'document_no', 'document_name',
              'effective_date', 'revision_no', 'revision_date', 'part_no', 'part_name','supplier_name',
              'customer_name', 'pdf_file', 'sheet_file', 'other_file']
    success_url = '/menu-dokumen/page/'
    

    def form_valid(self, form):
        # Perform custom validation
        nama_dok = form.cleaned_data.get('document')
        if MenuDokumen.objects.filter(document=nama_dok).exclude(pk=self.object.pk).exists():
            #form.add_error('document', ValidationError("A document with this name already exists."))
            return self.form_invalid(form)
        return super().form_valid(form)
    
class MenuDokumenEnableDisableView(UpdateView):

    def post(self, request, pk):
        menu_document_instance_update = MenuDokumen.objects.get(id=pk)
        set_aktif = request.POST.get('aktivasi')

        if set_aktif == "nonaktif":
            menu_document_instance_update.is_active = False
            menu_document_instance_update.save(update_fields=['is_active'])
        else:
            menu_document_instance_update.is_active = True
            menu_document_instance_update.save(update_fields=['is_active'])

        return redirect(self.request.META.get('HTTP_REFERER'))
    

class DokumenListView(ListView):
    model = Departemen
    template_name = 'DMSApp/CrudUploadDokumen/view.html'
    context_object_name = 'departemen_dokumen_list'

    def get_queryset(self):
        # Get the nama_dept from the request parameters
        nama_dept = self.request.GET.get('dept')

        if nama_dept:
            # Retrieve the Departemen object with the given department_id
            departemen = Departemen.objects.get(department=nama_dept)
                
            # Retrieve the related MenuDokumen objects for the Departemen
            queryset = departemen.menu_dokumen.all().order_by('document')
        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu_name = self.request.GET.get('menu')
        dept_name = self.request.GET.get('dept')
        if dept_name:
            # nm_directory = MenuDokumen.objects.get(sub_directory=menu_name)
            context['menu_dokumen'] = menu_name
            context['nm_department'] = dept_name
            context['menu_dokumen_list'] = MenuDokumen.objects.filter(document=menu_name)
        return context
    
class DokumenCreateView(CreateView):
    model = Dokumen
    template_name = 'DMSApp/CrudUploadDokumen/create.html'
    context_object_name = 'dokumen_list'
    # paginate_by = 10
    fields = ['no_form', 'no_dokumen', 'nama_dokumen', 'tanggal_efektif', 'no_revisi', 'tanggal_revisi', 'no_part', 'nama_part','nama_supplier', 'nama_customer']
    success_url = '/document/page'

    '''def get_queryset(self):
        # Assuming menu_name is available as a variable or passed through the URL
        menu_name = menu_name = self.request.GET.get('menu')
        queryset = super().get_queryset()
        return queryset.filter(document=menu_name)
'''
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu_name = self.request.GET.get('menu')
        dept_name = self.request.GET.get('dept')
        if menu_name:
            context['menu_dokumen'] = menu_name
            context['nm_department'] = dept_name
            context['menu_dokumen_list'] = MenuDokumen.objects.filter(document=menu_name)
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
        return queryset'''
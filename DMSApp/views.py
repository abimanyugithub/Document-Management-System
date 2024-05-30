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
        # Check if there is an existing Dokumen instance with the same no_dokumen and nama_dokumen
        existing_department = Departemen.objects.filter(department=nama_dept).exclude(id=pk).exists()
        
        if not existing_department:
            # Update other fields if there's no existing Dokumen instance with the same values
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
    

def add_menu(request):
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

class MenuDokumenListView(CreateView, ListView):
    model = MenuDokumen
    template_name = 'DMSApp/CrudMenuDokumen/view.html'
    context_object_name = 'menu_dokumen_list'  # For ListView
    fields = ['document', 'form_no', 'document_no', 'document_name',
              'effective_date', 'revision_no', 'revision_date', 'part_no', 'part_name','supplier_name',
              'customer_name', 'pdf_file', 'sheet_file', 'other_file']
    success_url = '/document/page'

    def get_queryset(self):
        return MenuDokumen.objects.order_by('document')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Specify the fields you want to render as checkboxes dynamically
        context['default_checked'] = ['document', 'effective_date', 'revision_no', 'revision_date', 'pdf_file', 'sheet_file']
        # context['doc_file'] = ['doc_pdf', 'doc_sheet', 'doc_additional']
        return context
    
'''class Viewadditional_fileView(ListView):
    model = additional_file
    template_name = 'DMSApp/CrudMenuDokumen/view.html'
    context_object_name = 'menu_dokumen_list'
    '''
    
class DokumenListView(CreateView, ListView):
    model = Dokumen
    template_name = 'DMSApp/CrudDokumen/view.html'
    context_object_name = 'dokumen_list'
    # paginate_by = 10
    fields = ['no_form', 'no_dokumen', 'nama_dokumen', 'tanggal_efektif', 'no_revisi', 'tanggal_revisi', 'no_part', 'nama_part','nama_supplier', 'nama_customer']
    success_url = '/document/page'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        directory_id = self.request.GET.get('directory_id')
        if directory_id:
            try:
                directory = MenuDokumen.objects.get(pk=directory_id)
                # Add conditions for other fields based on your needs
                # Example conditions (assuming similar boolean fields exist)
                if not directory.is_active:  # Adjust this condition based on your actual logic
                    form.fields.pop('no_form', None)
                    form.fields.pop('nama_part', None)
                    form.fields.pop('no_part', None)
                    form.fields.pop('nama_supplier', None)
            except MenuDokumen.DoesNotExist:
                pass
        return form
   
    def get_queryset(self):
        queryset = super().get_queryset()
        menu_name = self.request.GET.get('menu')
        dept_name = self.request.GET.get('dept')  # get the value of 'dept' parameter
        if menu_name:
            queryset = queryset.filter(directory__sub_directory=menu_name, dokumen_dept__nm_departemen=dept_name)
        return queryset
        
    '''
        # Process each item in the queryset
        for dl in queryset:
            # Use urljoin to create the full URL for file_pdf
            dl.file_pdf_url = urljoin(settings.MEDIA_URL, dl.file_pdf.url)

            # Extract the base names for file_pdf and file_sheet
            dl.file_pdf = os.path.basename(dl.file_pdf.name)
            dl.file_sheet = os.path.basename(dl.file_sheet.name)
        return queryset
    '''
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu_name = self.request.GET.get('menu')
        dept_name = self.request.GET.get('dept')
        if menu_name:
            nm_directory = MenuDokumen.objects.get(sub_directory=menu_name)
            context['sub_directory'] = nm_directory
            context['nm_department'] = dept_name
            context['departemen_list'] = Departemen.objects.all().order_by('nm_departemen')
        return context

    def form_valid(self, form):
        menu_name = self.request.GET.get('menu')
        dept_name = self.request.GET.get('dept')
        if menu_name and dept_name:
            nm_directory = MenuDokumen.objects.get(sub_directory=menu_name)
            department = Departemen.objects.get(nm_departemen=dept_name) 
            form.instance.directory = nm_directory
            form.instance.dokumen_dept = department
            form.instance.nama_file_pdf = form.cleaned_data['file_pdf']
            form.instance.nama_file_sheet = form.cleaned_data['file_sheet']
            # Define the directory path
            directory = os.path.join(folder_target, menu_name, dept_name)
            # Create the directory if it doesn't exist
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Save the form including the uploaded files
            form.instance.file_pdf.name = os.path.join(directory, form.instance.file_pdf.name)
            form.instance.file_sheet.name = os.path.join(directory, form.instance.file_sheet.name)
            form.save()
            
            '''with open(form.instance.file_pdf.name, 'wb+') as destination:
                for chunk in form.cleaned_data['file_pdf'].chunks():
                    destination.write(chunk)
                    
            with open(form.instance.file_sheet.name, 'wb+') as destination:
                for chunk in form.cleaned_data['file_sheet'].chunks():
                    destination.write(chunk)'''

            response = super().form_valid(form)
        # Redirect to the dokumen_view URL with the menu parameter
        # return redirect(reverse('dokumen_view') + f'?menu={self.request.GET.get("menu")}')
        return redirect(self.request.META.get('HTTP_REFERER'))
    
class DokumenUpdateView(UpdateView):
    model = Dokumen
    fields = ['no_dokumen', 'nama_dokumen', 'tanggal_efektif', 'no_revisi', 'tanggal_revisi', 'file_pdf', 'file_sheet']
    
    def post(self, request, pk):
        dokumen_instance_update = Dokumen.objects.get(id=pk)
        menu_name = self.request.GET.get('menu')
        dept_name = self.request.GET.get('dept')
        # Define the directory path
        directory = os.path.join(folder_target, menu_name, dept_name)
        no_dokumen = request.POST.get('no_dokumen')
        nama_dokumen = request.POST.get('nama_dokumen')
        
        # Check if there is an existing Dokumen instance with the same no_dokumen and nama_dokumen
        existing_dokumen = Dokumen.objects.filter(no_dokumen=no_dokumen, nama_dokumen=nama_dokumen).exclude(id=pk).exists()
        
        if not existing_dokumen:
            # Update other fields if there's no existing Dokumen instance with the same values
            for field in self.fields:
                if request.POST.get(field):
                    setattr(dokumen_instance_update, field, request.POST.get(field))

            # Handle FileField updates
            if 'file_pdf' in request.FILES:
                # Overwrite existing file or delete if new file is None
                if dokumen_instance_update.file_pdf:
                    os.remove(dokumen_instance_update.file_pdf.path)
                file_pdf = request.FILES['file_pdf']
                dokumen_instance_update.file_pdf.save(os.path.join(directory, file_pdf.name), file_pdf, save=False)
            if 'file_sheet' in request.FILES:
                # Overwrite existing file or delete if new file is None
                if dokumen_instance_update.file_sheet:
                    os.remove(dokumen_instance_update.file_sheet.path)
                file_sheet = request.FILES['file_sheet']
                dokumen_instance_update.file_sheet.save(os.path.join(directory, file_sheet.name), file_sheet, save=False)

            dokumen_instance_update.save(update_fields=self.fields)
            
        return redirect(self.request.META.get('HTTP_REFERER'))
    

class DokumenDeleteView(DeleteView):
    
    def post(self, request, pk):
        document_instance_delete = Dokumen.objects.get(id=pk)
        # Get the file paths from the file_pdf and file_sheet fields
        file_pdf_path = document_instance_delete.file_pdf.path
        file_sheet_path = document_instance_delete.file_sheet.path

        # Delete the files if they exist
        if os.path.exists(file_pdf_path):
            os.remove(file_pdf_path)
        if os.path.exists(file_sheet_path):
            os.remove(file_sheet_path)
        # Delete the Dokumen object
        document_instance_delete.delete()

        return redirect(self.request.META.get('HTTP_REFERER'))
        
'''class SOPFlowListView(ListView):
    model = Departemen
    template_name = 'FMS/view.html'
    context_object_name = 'departemen_list'  # For ListView


class CreateDokumen(CreateView):
    model = Dokumen
    template_name = 'FMS/create.html'
    context_object_name = 'departemen_list'  # For ListView
    

class DokumenListView(CreateView, ListView):
    model = Dokumen
    template_name = 'FMS/list.html'
    context_object_name = 'dokument_list'
    paginate_by = 10
    fields = ['id_dokumen', 'nm_dokumen']
    success_url = '/fms/sop-flow/dokumen/'

    def get_queryset(self):
        queryset = super().get_queryset()
        dept_name = self.request.GET.get('dept')
        if dept_name:
            queryset = queryset.filter(dokumen_dept=dept_name)
        return queryset

    def form_valid(self, form):
        dept_name = self.request.GET.get('dept')
        if dept_name:
            form.instance.dokumen_dept_name = dept_name
        return super().form_valid(form)
'''


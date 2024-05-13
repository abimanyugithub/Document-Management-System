from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from .models import MenuDokumen, Departemen, Dokumen
from django.shortcuts import redirect
import os

folder_target = 'media/DMSApp/'
# Create your views here.
class DashboardView(TemplateView):
    template_name = 'DMSApp/Komponen/dashboard.html'


class DepartemenListView(CreateView, ListView):
    model = Departemen
    template_name = 'DMSApp/CrudDepartemen/view.html'
    context_object_name = 'departemen_list'  # For ListView
    fields = ['nm_departemen', 'nm_perusahaan', 'deskripsi']
    success_url = '/departemen/page/'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('nm_departemen')
    
    def form_valid(self, form):
        # Custom form validation
        nm_departemen = form.cleaned_data['nm_departemen']
        if Departemen.objects.filter(nm_departemen=nm_departemen).exists():
            form.add_error('nm_departemen', "A department with this name already exists.")
            return self.form_invalid(form)
        return super().form_valid(form)

class DepartemenUpdateView(UpdateView):
    
    def post(self, request, pk):
        department_instance_update = Departemen.objects.get(nm_departemen=pk)
        nama_dept = request.POST.get('nm_departemen')
        nama_pt = request.POST.get('nm_perusahaan')
        desc = request.POST.get('deskripsi')

        if nama_dept:
            if not Departemen.objects.filter(nm_departemen=nama_dept).exists():
                department_instance_update.nm_departemen = nama_dept

        if nama_pt or desc:
            department_instance_update.nm_perusahaan = nama_pt
            department_instance_update.deskripsi = desc

        department_instance_update.save(update_fields=['nm_departemen', 'nm_perusahaan', 'deskripsi'])

        return redirect(self.request.META.get('HTTP_REFERER'))

class DepartemenEnableDisableView(UpdateView):

    def post(self, request, pk):
        department_instance_update = Departemen.objects.get(nm_departemen=pk)
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
        if new_menu_name:
            if not MenuDokumen.objects.filter(sub_directory=new_menu_name).exists():
                MenuDokumen.objects.create(sub_directory=new_menu_name)
                # Define the directory path
                directory = folder_target + new_menu_name
                # Create the directory if it doesn't exist
                if not os.path.exists(directory):
                    os.makedirs(directory)
                # return JsonResponse({'success': True, 'menu_name': menu.name})
            
    return redirect(request.META.get('HTTP_REFERER'))

class DokumenListView(CreateView, ListView):
    model = Dokumen
    template_name = 'DMSApp/CrudDokumen/view.html'
    context_object_name = 'dokumen_list'
    # paginate_by = 10
    fields = ['no_dokumen', 'nama_dokumen', 'tanggal_efektif', 'revisi_no', 'tanggal_revisi', 'file_pdf', 'file_sheet']
    success_url = '/document/page'

    def get_queryset(self):
        queryset = super().get_queryset()
        menu_name = self.request.GET.get('menu')
        dept_name = self.request.GET.get('dept')  # get the value of 'dept' parameter
        if menu_name:
            queryset = queryset.filter(directory__sub_directory=menu_name, dokumen_dept__nm_departemen=dept_name)
        else:
            pass

        # Extracting file names only for file_pdf and file_sheet
        for dl in queryset:
            dl.file_pdf = os.path.basename(dl.file_pdf.name)
            dl.file_sheet = os.path.basename(dl.file_sheet.name)
        return queryset
    
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
            directory = folder_target + menu_name + '/' + dept_name
            # Create the directory if it doesn't exist
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Save the form including the uploaded files
            form.instance.file_pdf.name = os.path.join(directory, form.instance.file_pdf.name)
            form.instance.file_sheet.name = os.path.join(directory, form.instance.file_sheet.name)
            form.save()
            
            with open(form.instance.file_pdf.name, 'wb+') as destination:
                for chunk in form.cleaned_data['file_pdf'].chunks():
                    destination.write(chunk)
                    
            with open(form.instance.file_sheet.name, 'wb+') as destination:
                for chunk in form.cleaned_data['file_sheet'].chunks():
                    destination.write(chunk)

            response = super().form_valid(form)
        # Redirect to the dokumen_view URL with the menu parameter
        # return redirect(reverse('dokumen_view') + f'?menu={self.request.GET.get("menu")}')
        return redirect(self.request.META.get('HTTP_REFERER'))
    
class DokumenUpdateView(UpdateView):
    model = Dokumen
    fields = ['no_dokumen', 'nama_dokumen', 'tanggal_efektif', 'revisi_no', 'tanggal_revisi', 'file_pdf', 'file_sheet']
    
    def post(self, request, pk):
        dokumen_instance_update = Dokumen.objects.get(id=pk)

        no_dokumen = request.POST.get('no_dokumen')
        nama_dokumen = request.POST.get('nama_dokumen')
        
        # Check if there is an existing Dokumen instance with the same no_dokumen and nama_dokumen
        existing_dokumen = Dokumen.objects.filter(no_dokumen=no_dokumen, nama_dokumen=nama_dokumen).exclude(id=pk).exists()
        
        if not existing_dokumen:
            # Update other fields if there's no existing Dokumen instance with the same values
            for field in self.fields:
                if request.POST.get(field):
                    setattr(dokumen_instance_update, field, request.POST.get(field))
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


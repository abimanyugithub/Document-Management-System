from itertools import chain
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView, DetailView, FormView
from .models import Dokumen, Departemen, DokumenLabel, Arsip
from django.conf import settings
from urllib.parse import urljoin
import os, shutil
from django import forms
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import PermissionDenied, ValidationError
from django.urls import reverse
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin

folder_target = 'media/DMSApp/'

daftar_label = [{'form_no': {"label": "Form Number", "type": "text"},
                'document_no': {"label": "Document ID", "type": "text"},
                'document_name': {"label": "Document Title", "type": "text"},
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
    
'''class LDAPUsernameForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)

# Create your views here.
class LoginView(FormView):
    template_name = 'DMSApp/Komponen/login.html'
    form_class = LDAPUsernameForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        
        # LDAP settings
        LDAP_SERVER_URI = settings.AUTH_LDAP_SERVER_URI
        BIND_DN = settings.AUTH_LDAP_BIND_DN
        BIND_PASSWORD = settings.AUTH_LDAP_BIND_PASSWORD
        USER_SEARCH_BASE = "ou=Departments,dc=fln,dc=local"
        SEARCH_FILTER = "(sAMAccountName=%(user)s)"  # Filter for sAMAccountName
        
        try:
            # Initialize LDAP connection
            conn = ldap.initialize(LDAP_SERVER_URI)
            conn.simple_bind_s(BIND_DN, BIND_PASSWORD)
            
            # Search for the user
            result = conn.search_s(USER_SEARCH_BASE, ldap.SCOPE_SUBTREE, SEARCH_FILTER % {'user': username})
            
            if result:
                # User found in LDAP
                return render(self.request, 'DMSApp/Komponen/dashboard.html', {'username': username})
            else:
                # User not found in LDAP
                return render(self.request, 'ldap_username_invalid.html', {'username': username})
        
        except ldap.LDAPError as e:
            # LDAP connection or search error
            return render(self.request, 'ldap_error.html', {'error_message': f"LDAP search failed: {e}"})
'''

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'DMSApp/Komponen/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for label_dict in daftar_label:
            context['list_label'] = label_dict
        arsip_list = Arsip.objects.filter(is_active=True, is_approved=True).order_by('document_no','-revision_no')

        # Use Python to filter out duplicates based on document_no
        unique_arsip_list = []
        seen_document_nos = set()
        for arsip in arsip_list:
            if arsip.document_no not in seen_document_nos:
                unique_arsip_list.append(arsip)
                seen_document_nos.add(arsip.document_no)
        context['arsip_list'] = unique_arsip_list

        '''# LDAP search details
        LDAP_SERVER_URI = settings.AUTH_LDAP_SERVER_URI
        BIND_DN = settings.AUTH_LDAP_BIND_DN
        BIND_PASSWORD = settings.AUTH_LDAP_BIND_PASSWORD
        USER_SEARCH_BASE = "ou=Departments,dc=fln,dc=local"
        SEARCH_FILTER = "(objectClass=person)"  # Fetch all users

        # Perform LDAP search
        try:
            conn = ldap.initialize(LDAP_SERVER_URI)
            conn.simple_bind_s(BIND_DN, BIND_PASSWORD)
            result = conn.search_s(USER_SEARCH_BASE, ldap.SCOPE_SUBTREE, SEARCH_FILTER)
            
            # Pass the search result to the context
            context['ldap_results'] = result
        except ldap.LDAPError as e:
            context['ldap_error'] = f"LDAP search failed: {e}"'''
        
        '''# LDAP search details
        LDAP_SERVER_URI = settings.AUTH_LDAP_SERVER_URI
        BIND_DN = settings.AUTH_LDAP_BIND_DN
        BIND_PASSWORD = settings.AUTH_LDAP_BIND_PASSWORD
        USER_SEARCH_BASE = "ou=Departments,dc=fln,dc=local"
        SEARCH_FILTER = "(objectClass=user)"  # Filter for user objects

        # Attributes to retrieve
        ATTRIBUTES = ['sAMAccountName']

        # Perform LDAP search
        try:
            conn = ldap.initialize(LDAP_SERVER_URI)
            conn.simple_bind_s(BIND_DN, BIND_PASSWORD)
            result = conn.search_s(USER_SEARCH_BASE, ldap.SCOPE_SUBTREE, SEARCH_FILTER, ATTRIBUTES)
            
            # Extract sAMAccountName and pass to context
            account_names = []
            for dn, entry in result:
                if 'sAMAccountName' in entry:
                    account_names.append(entry['sAMAccountName'][0].decode('utf-8'))
            
            # Pass the account names to the context
            context['account_names'] = account_names
        except ldap.LDAPError as e:
            context['ldap_error'] = f"LDAP search failed: {e}"'''

        return context


class DepartemenListView(CreateView, ListView): # CreateView show in modal
    model = Departemen
    template_name = 'DMSApp/CrudDepartemen/view.html'
    context_object_name = 'departemen_list'  # For ListView
    fields = ['department', 'department_code', 'company', 'address']
    success_url = '/department/page'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('department')
    
    def form_valid(self, form):
        # Custom form validation
        nma_departemen = form.cleaned_data['department']
        kode_departemen = form.cleaned_data['department_code']
        
        if Departemen.objects.filter(department=nma_departemen).exists():
            form.add_error('department', "A department with this name already exists.")
            return self.form_invalid(form)

        if Departemen.objects.filter(department_code=kode_departemen).exists():
            form.add_error('department_code', "A department with this code already exists.")
            return self.form_invalid(form)
        
        # If validation passes, save the department
        departemen = form.save(commit=False)
        departemen.save()
        
        # Handle related documents
        selected_dokumen_ids = self.request.POST.getlist('checklist_dokumen')
        dokumen = Dokumen.objects.filter(id__in=selected_dokumen_ids)
        departemen.related_document.set(dokumen)

        return redirect(self.request.META.get('HTTP_REFERER'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_dokumen'] = Dokumen.objects.filter(is_active=True)
        fields = {'department': 'Department', 'department_code': 'Department Code', 'company': 'Company', 'address': 'Address', 'created_date': 'Created Date', 'modified_date': 'Modified Date'} # Fields to display
        context['fields'] = fields
        # context['fields'] = [field.name for field in self.model._meta.get_fields()]
        return context


class DepartemenUpdateView(UpdateView): # Show in modal
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
            except:
                print(f"Dokumen with id {dok_id} does not exist.")

        return redirect(self.request.META.get('HTTP_REFERER'))
    

class DepartemenActivateDeactivateView(UpdateView): # Show in modal

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
    

class DepartemenDeleteView(DeleteView): # Show in modal

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
    


class DokumenListView(CreateView, ListView): # CreateView show in modal
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
        fields = {'document': 'Document', 'document_initial': 'Document Initial', 'created_date': 'Created Date', 'modified_date': 'Modified Date'} # Fields to display
        context['fields'] = fields

        for label_dict in daftar_label:
            context['list_label'] = label_dict
            
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
            

class DokumenUpdateView(UpdateView): # Show in modal
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
                form.add_error('department', "A dokumen with this name already exists.")
            if inisial_dokumen_yang_ada:
                form.add_error('inisial_dokumen', "A dokumen with this initial already exists.")
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
        try:
            old_folder_path = os.path.join(folder_target, current_document_name)
            new_folder_path = os.path.join(folder_target, nma_dokumen)
            
            if os.path.exists(old_folder_path):
                os.rename(old_folder_path, new_folder_path)
            else:
                print(f"The directory '{old_folder_path}' does not exist.")
        except:
            print(f"Dokumen with id does not exist.")

        return redirect(self.request.META.get('HTTP_REFERER'))
    '''
        old_folder_path = os.path.join(folder_target, current_document_name)
        new_folder_path = os.path.join(folder_target, nma_dokumen)
        os.rename(old_folder_path, new_folder_path)

        return redirect(self.request.META.get('HTTP_REFERER'))'''


class DokumenActivateDeactivateView(UpdateView): # Show in modal

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
    
class DokumenDeleteView(DeleteView): # Show in modal

    def post(self, request, pk):
        dokumen_instance_delete = Dokumen.objects.get(id=pk)

        # Check if there is an existing
        if Arsip.objects.filter(parent_document=pk).exists():
            # If related Arsip instances exist, raise PermissionDenied
            raise PermissionDenied("Cannot delete this document because related Arsip instances exist.")

        # Construct the path to the directory
        path = os.path.join(folder_target, dokumen_instance_delete.document)

        if os.path.exists(path):
            shutil.rmtree(path)

        dokumen_instance_delete.delete()

        return redirect(self.request.META.get('HTTP_REFERER'))
    

class ArsipListView(ListView):
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
                
                # context['arsip_listx'] = Arsip.objects.filter(parent_document__document=nma_dokumen, parent_department__department=nma_departemen, is_active=True).values('document_no').distinct()
                
                # Fetch the queryset
                arsip_list = Arsip.objects.filter(parent_document__document=nma_dokumen, parent_department__department=nma_departemen).order_by('document_no', '-revision_no')

                # Use Python to filter out duplicates based on document_no
                unique_arsip_list = []
                seen_document_nos = set()
                for arsip in arsip_list:
                    if arsip.document_no not in seen_document_nos:
                        unique_arsip_list.append(arsip)
                        seen_document_nos.add(arsip.document_no)

                context['arsip_list'] = unique_arsip_list

                for label_dict in daftar_label:
                    context['list_label'] = label_dict
        return context
    

# contoh penomoran dokumen => 2. FMS.31.01 REV.02_MEMBUAT TAGIHAN CUSTOMER 8. FMS.31.05.02 REV.02_PPH 21 
class ArsipCreateView(CreateView): # Revision juga menggunakan class ini
    model = Arsip
    template_name = 'DMSApp/CrudArsip/create.html'
    fields = []  # Remove fields, as we are handling them manually

    def form_valid(self, form):
        # Get the values of menu1 and dept1 from the form
        nma_dokumen = self.request.POST.get('dokumen')
        nma_departemen = self.request.POST.get('departemen')
        nma_arsip = self.request.POST.get('document_name')
        no_arsip = self.request.POST.get('document_no')
        no_form = self.request.POST.get('form_no')
        no_revisi = self.request.POST.get('revision_no')
        
        # Retrieve IDs from the database based on the names
        dokumen_obj = Dokumen.objects.get(document=nma_dokumen)  
        departemen_obj = Departemen.objects.get(department=nma_departemen)

        # Get the values revision
        nma_arsip = self.request.GET.get('archive')

        if nma_arsip:
            # Check if a document name and revision no with the same name already exists
            if Arsip.objects.filter(document_name=nma_arsip, revision_no=no_revisi).exists():
                raise ValidationError('An entry with this revision number already exists.')
        elif no_arsip:
            # Check if a document name or document no with the same name already exists
            if Arsip.objects.filter(document_name=nma_arsip).exists() or Arsip.objects.filter(document_no=no_arsip).exists():
                raise ValidationError('An entry with this document name or document number already exists.')
            
        elif no_form:
            # Check if a document name or form no with the same name already exists
            if Arsip.objects.filter(document_name=nma_arsip).exists() or Arsip.objects.filter(form_no=no_form).exists():
                raise ValidationError('An entry with this document name or form number already exists.')
        
        # Set the IDs to the form instance before saving
        form.instance.parent_document = dokumen_obj
        form.instance.parent_department = departemen_obj

        # Save the form
        self.object = form.save()

        # Handle saving dynamic fields and files
        # directory = os.path.join(folder_target, 'temporary', nma_dokumen, nma_departemen)
        directory = os.path.join(folder_target, nma_dokumen, nma_departemen)
        
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
                        setattr(self.object, key, os.path.join(directory, filename))
                        # setattr(self.object, key, filename)
                        
                else:

                    # Get the value of the field from the request
                    field_value = self.request.POST.get(key)
                    setattr(self.object, key, field_value)
        
        # Now save the instance to the database
        self.object.save()

        # Construct the success URL dynamically
        success_url = reverse('arsip_view') + f"?menu={nma_dokumen}&dept={nma_departemen}"

        # Redirect to the success URL
        return redirect(success_url)
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nma_dokumen = self.request.GET.get('menu')
        nma_departemen = self.request.GET.get('dept')

        # get_context_data for revision
        nma_arsip = self.request.GET.get('archive')

        if nma_dokumen:
            # Retrieve the related MenuDokumen objects for the Departemen
            nma_label = Dokumen.objects.get(document=nma_dokumen)
            relasi_label = nma_label.related_label.all()
            context['nm_dokumen'] = nma_dokumen
            context['nm_departemen'] = nma_departemen
            context['nm_arsip'] = nma_arsip
            kode_arsip = Arsip.objects.filter(document_name=nma_arsip, is_active=True)
            for i in kode_arsip:
                context['kode_arsip'] = i.document_no +' REV. '+ i.revision_no
            context['nm_label'] = relasi_label
            # context['list_label'] = daftar_label
            context['nma_inisial'] = nma_label.document_initial

            for label_dict in daftar_label:
                context['list_label'] = label_dict

            username = self.request.user.username  # Adjust as per your user model or LDAP attribute
            context['username'] = username
                
            # get_context_data for revision
            if nma_arsip:
                context['archive_list'] = Arsip.objects.filter(parent_document__document=nma_dokumen, parent_department__department=nma_departemen, document_name=nma_arsip)

        return context
    

class ArsipUpdateView(UpdateView):
    model = Arsip
    template_name = 'DMSApp/CrudArsip/update.html'
    fields = []  # Remove fields, as we are handling them manually
    success_url = '/department/page/'

    def post(self, request, pk):
        # Retrieve the Arsip instance to update
        archive_instance_update = Arsip.objects.get(id=pk)
        directory = os.path.join(
            folder_target,
            archive_instance_update.parent_document.document,
            archive_instance_update.parent_department.department
        )
        
        # Check and handle pdf_file
        if 'pdf_file' in request.FILES:
            # archive_instance_update.pdf_file = request.FILES['pdf_file']
            if archive_instance_update.pdf_file:
                os.remove(archive_instance_update.pdf_file.path)
            file_pdf = request.FILES['pdf_file']
            archive_instance_update.pdf_file.save(os.path.join(directory, file_pdf.name), file_pdf, save=False)

        # Check and handle sheet_file
        if 'sheet_file' in request.FILES:
            # archive_instance_update.sheet_file = request.FILES['sheet_file']
            if archive_instance_update.sheet_file:
                os.remove(archive_instance_update.sheet_file.path)
            file_sheet = request.FILES['sheet_file']
            archive_instance_update.sheet_file.save(os.path.join(directory, file_sheet.name), file_sheet, save=False)


        # Check and handle other_file
        if 'other_file' in request.FILES:
            # archive_instance_update.other_file = request.FILES['other_file']
            if archive_instance_update.other_file:
                os.remove(archive_instance_update.other_file.path)
            file_other = request.FILES['other_file']
            archive_instance_update.other_file.save(os.path.join(directory, file_other.name), file_other, save=False)

        # Iterate over POST data
        for key, value in request.POST.items():
            if key not in ['pdf_file', 'sheet_file', 'add_file'] and hasattr(archive_instance_update, key):
                setattr(archive_instance_update, key, value)

        # Save the updated Arsip instance
        archive_instance_update.save()

        return redirect(self.request.META.get('HTTP_REFERER'))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nma_dokumen = self.request.GET.get('menu')
        nma_departemen = self.request.GET.get('dept')

        # get_context_data for update
        nma_arsip = self.request.GET.get('archive')

        # Retrieve the related MenuDokumen objects for the Departemen
        nma_label = Dokumen.objects.get(document=nma_dokumen)
        relasi_label = nma_label.related_label.all()
        context['nm_dokumen'] = nma_dokumen
        context['nm_departemen'] = nma_departemen
        context['nm_arsip'] = nma_arsip
        kode_arsip = Arsip.objects.filter(document_name=nma_arsip, is_active=True)
        for i in kode_arsip:
            context['kode_arsip'] = i.document_no +' REV. '+ i.revision_no
        context['nm_label'] = relasi_label

        for label_dict in daftar_label:
            context['list_label'] = label_dict
            
        # get_context_data for update
        context['archive_detail'] = self.object

        return context


class ArsipDetailView(DetailView): 
    model = Arsip
    template_name = 'DMSApp/CrudArsip/detail.html'  # You can customize the template name if needed
    context_object_name = 'archive_detail'  # Specify the name of the variable to be used in the template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nma_dokumen = self.request.GET.get('menu')
        nma_departemen = self.request.GET.get('dept')
        nma_arsip = self.request.GET.get('archive')
        if nma_dokumen:
            # Retrieve the related MenuDokumen objects for the Departemen
            nma_label = Dokumen.objects.get(document=nma_dokumen)
            relasi_label = nma_label.related_label.all()
            context['nm_dokumen'] = nma_dokumen
            context['nm_departemen'] = nma_departemen
            context['nm_arsip'] = nma_arsip
            kode_arsip = Arsip.objects.filter(document_name=nma_arsip, is_active=True)
            for i in kode_arsip:
                context['kode_arsip'] = i.document_no +' REV. '+ i.revision_no
            context['nm_label'] = relasi_label

            for label_dict in daftar_label:
                context['list_label'] = label_dict
        return context
    
    
class ArsipDeleteView(DeleteView): # show in modal

    def post(self, request, pk):
        archive_instance_delete = Arsip.objects.get(id=pk)
        
        # Delete the model instance
        archive_instance_delete.delete()
        
        fs = FileSystemStorage()

        # List of file fields to check and delete
        file_fields = ['pdf_file', 'sheet_file', 'other_file']

        # Iterate through each file field and delete if it exists
        for file_field in file_fields:
            file = getattr(archive_instance_delete, file_field)
            if file and file.name:  # Check if the file field has a file
                file_path = file.path
                if fs.exists(file_path):
                    fs.delete(file_path)
                    print(f"{file_path} has been deleted.")
                else:
                    print(f"{file_path} does not exist.")

        return redirect(self.request.META.get('HTTP_REFERER'))


class ArsipDetailListView(ListView):
    model = Arsip
    template_name = 'DMSApp/CrudArsip/view_detail.html'
    context_object_name = 'archive_list'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Get filter parameters from the GET request
        nma_dokumen = self.request.GET.get('menu')
        nma_departemen = self.request.GET.get('dept')
        nma_arsip = self.request.GET.get('archive')

        # Apply filters if parameters are provided
        queryset = queryset.filter(document_name=nma_arsip, parent_document__document=nma_dokumen, parent_department__department=nma_departemen).order_by('-revision_no')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nma_dokumen = self.request.GET.get('menu')
        nma_departemen = self.request.GET.get('dept')
        nma_arsip = self.request.GET.get('archive')
        if nma_dokumen:
            # Retrieve the related MenuDokumen objects for the Departemen
            nma_label = Dokumen.objects.get(document=nma_dokumen)
            relasi_label = nma_label.related_label.all()
            context['nm_dokumen'] = nma_dokumen
            context['nm_departemen'] = nma_departemen
            context['nm_arsip'] = nma_arsip
            context['nm_label'] = relasi_label

            context['is_unapproved_instances'] = Arsip.objects.filter(
                document_name=nma_arsip,
                parent_document__document=nma_dokumen,
                parent_department__department=nma_departemen,
                is_approved=False
            ).exists()

        for label_dict in daftar_label:
            context['list_label'] = label_dict

        return context
    

class ArchiveUpdateStatusView(UpdateView): # Show in modal

    def post(self, request, pk):
        archive_instance_update = Arsip.objects.get(id=pk)
        opsi_aktivasi = request.POST.get('status')

        if opsi_aktivasi == "pending":
            archive_instance_update.is_inprogress = True
            archive_instance_update.save(update_fields=['is_inprogress'])

        elif opsi_aktivasi == "inprogress":
            # Update other instances where is_active is True to False
            Arsip.objects.exclude(id=pk).filter(is_active=True, document_no=archive_instance_update.document_no).update(is_active=False)

            archive_instance_update.is_approved = True
            archive_instance_update.is_inprogress = False
            archive_instance_update.save(update_fields=['is_inprogress', 'is_approved'])

        else:
            archive_instance_update.is_rejected = True
            archive_instance_update.is_inprogress = False
            archive_instance_update.save(update_fields=['is_rejected', 'is_inprogress'])

        return redirect(self.request.META.get('HTTP_REFERER'))


class ArsipActivateDeactivateView(UpdateView): # Show in modal

    def post(self, request, pk):
        archive_instance_update = Arsip.objects.get(id=pk)
        opsi_aktivasi = request.POST.get('aktivasi')

        if opsi_aktivasi == "nonaktif":
            archive_instance_update.is_active = False
            archive_instance_update.save(update_fields=['is_active'])
        else:
            # Update other instances where is_active is True to False
            Arsip.objects.exclude(id=pk).filter(is_active=True, document_no=archive_instance_update.document_no).update(is_active=False)

            archive_instance_update.is_active = True
            archive_instance_update.save(update_fields=['is_active'])

        return redirect(self.request.META.get('HTTP_REFERER'))


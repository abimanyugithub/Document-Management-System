from itertools import chain
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView, DetailView, View
from .models import KategoriDokumen, Departemen, KategoriDokumenLabel, Arsip, UserDetail
from django.conf import settings
from urllib.parse import urljoin
import os, shutil
from django import forms
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import PermissionDenied, ValidationError
from django.urls import reverse
from django.db.models import Count, Max
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout, authenticate
import ldap
from django_auth_ldap.backend import LDAPBackend

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
class LoginView(LoginView):
    template_name = 'DMSApp/Komponen/login.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated and self.request.user.is_active:
            return redirect('/')  # Redirect to the home page if already authenticated
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        # First try LDAP authentication
        ldap_backend = LDAPBackend()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = None
        try:
            user = ldap_backend.authenticate(self.request, username=username, password=password)
        except ldap.LDAPError as e:
            print(f"LDAP authentication error: {e}")
            pass

        # If LDAP authentication fails, fall back to the default model backend
        if user is None:
            user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect(self.get_success_url())
        else:
            # Optionally, you can log the failure reason or take some other action
            return self.form_invalid(form)
        
class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)
    
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
            
        '''
        
        # LDAP search details
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
    
class AkunRegisterView(CreateView):
    model = UserDetail
    template_name = 'DMSApp/CrudAkun/register.html'
    fields = ['username', 'first_name', 'last_name', 'email', 'password']
    success_url = '/account/page/'

    def form_valid(self, form):
        if self.request.user.is_superuser or not UserDetail.objects.filter(is_superuser=True, is_active=True):
            password = form.cleaned_data['password']
            confirm_password = self.request.POST.get('password2')

            # Check if passwords match
            if password == confirm_password:
                # Hash the password before saving
                form.instance.set_password(form.cleaned_data['password'])
                form.instance.is_ldap = False

                # if superuser not exist
                if not UserDetail.objects.filter(is_superuser=True, is_active=True):
                    form.instance.is_superuser = True
                    self.object = form.save()
                    # if form.cleaned_data.get('username'):
                    # return redirect('/')self.success_url
                    return redirect(self.success_url)
            else:
                return redirect(self.request.META.get('HTTP_REFERER'))
            
            return super().form_valid(form)
        else:
            raise PermissionDenied("Cannot update this account because it is a superuser.")
        

class AkunListView(LoginRequiredMixin, CreateView, ListView): # CreateView as Update in modal
    model = UserDetail
    template_name = 'DMSApp/CrudAkun/view.html'
    context_object_name = 'user_list'  # For ListView
    fields = ['user_department', 'first_name', 'last_name' , 'email', 'is_uploader', 'is_releaser', 'is_approver', 'is_superuser' ]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Check if the user is a superuser
        if not self.request.user.is_superuser:
            # List of fields to remove
            fields_to_remove = ['first_name', 'last_name', 'email', 'is_superuser']
            for field in fields_to_remove:
                form.fields.pop(field, None)
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # For Fields to display ListView
        fields_view = {'username': 'Username', 'first_name': 'First Name', 'last_name': 'Last Name', 'email': 'Email', 'user_department': 'Department', 'is_uploader': 'Upload', 'is_releaser': 'Release', 'is_approver': 'Approve', 'is_superuser':'Superuser' } # Fields to display
        
        # For Fields Update
        fields_boolean = {'is_uploader': 'Upload', 'is_releaser': 'Release', 'is_approver': 'Approve', 'is_superuser':'Superuser' }
        
        # If list user(s) not a superuser
        if not self.object_list.filter(is_superuser=True, is_active=True):
            context['fields_boolean'] = fields_boolean
            context['fields'] = fields_view

        # Remove 'is_superuser' if the user is not a superuser
        elif not self.request.user.is_superuser:
            fields_boolean.pop('is_superuser')
            fields_view.pop('is_superuser')

        context['fields_boolean'] = fields_boolean
        context['fields'] = fields_view
        context['list_department'] = Departemen.objects.all()
        # context['superuser_exist'] = self.object_list.filter(is_superuser=True, is_active=True)
        # context['fields'] = [field.name for field in self.model._meta.get_fields()]
        return context

class AkunUpdateView(UpdateView): # Show in modal
    model = UserDetail
    fields = []
    
    def post(self, request, pk):
        if self.request.user.is_superuser or self.request.user.is_releaser or not UserDetail.objects.filter(is_superuser=True, is_active=True):
            user_instance_update = UserDetail.objects.get(id=pk)
            id_departemen = request.POST.get('user_department')
            nma_depan = request.POST.get('first_name')
            nma_belakang = request.POST.get('last_name')
            surel = request.POST.get('email')

            # Retrieve the Departemen instance based on id_departemen
            # departemen_instance = Departemen.objects.get(id=id_departemen)
            
            # Assign the Departemen instance to user_department
            if id_departemen:
                user_instance_update.user_department = Departemen.objects.get(id=id_departemen)
            if nma_depan:
                user_instance_update.first_name = nma_depan
            if nma_belakang:
                user_instance_update.last_name = nma_belakang
            if surel:
                user_instance_update.email = surel
                
            # Retrieve all possible keys for checkboxes
            possible_keys = ['is_approver', 'is_releaser', 'is_uploader', 'is_superuser']

            # Iterate over all possible keys
            for key in possible_keys:
                # Set attribute to True if key is in request.POST.getlist('checklist_label'), otherwise set to False
                setattr(user_instance_update, key, key in request.POST.getlist('checklist_label'))

            # Save the updated instance
            user_instance_update.save()
            
            return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            raise PermissionDenied("Cannot update this account because it is a superuser.")

class AkunActivateDeactivateView(UpdateView): # Show in modal

    def post(self, request, pk):

        if self.request.user.is_superuser:
            account_instance_update = UserDetail.objects.get(id=pk)
            opsi_aktivasi = request.POST.get('aktivasi')
            if opsi_aktivasi == "nonaktif":
                account_instance_update.is_active = False
                account_instance_update.save(update_fields=['is_active'])
            else:
                account_instance_update.is_active = True
                account_instance_update.save(update_fields=['is_active'])
            return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            raise PermissionDenied("Cannot update this account because it is a superuser.")
        

class AkunDeleteView(DeleteView): # Show in modal

    def post(self, request, pk):
        if self.request.user.is_superuser:
            user_instance_delete = UserDetail.objects.get(id=pk)
            user_instance_delete.delete()
            return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            raise PermissionDenied("Cannot delete this account because it is a superuse")
        

class DepartemenListView(CreateView, ListView): # CreateView show in modal
    model = Departemen
    template_name = 'DMSApp/CrudDepartemen/view.html'
    context_object_name = 'departemen_list'  # For ListView
    fields = ['department', 'department_code', 'company', 'address']
    success_url = '/department/page/'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('department')
    
    def form_valid(self, form):
        # Get the data from the form
        if self.request.user.is_superuser or self.request.user.is_releaser:
            kode_department = form.cleaned_data['department_code']

            if Departemen.objects.filter(department=form.cleaned_data['department']).exists():
                # Raise PermissionDenied if a duplicate department is found
                raise PermissionDenied("Cannot create this department because an instance with the same department already exists.")
            if kode_department:
                if Departemen.objects.filter(department_code=form.cleaned_data['department_code']).exists():
                    raise PermissionDenied("Cannot create this department because an instance with the same department code already exists.")

            # If validation passes, save the department
            departemen = form.save()
            
            # Handle related category
            selected_dokumen_ids = self.request.POST.getlist('checklist_dokumen')
            kategori = KategoriDokumen.objects.filter(id__in=selected_dokumen_ids)
            departemen.related_category.set(kategori)

            return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            raise PermissionDenied("You do not have the necessary permissions.")
            
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_dokumen'] = KategoriDokumen.objects.filter(is_active=True)
        fields = {'department': 'Department', 'department_code': 'Department Code', 'company': 'Company', 'address': 'Address', 'created_date': 'Created Date', 'modified_date': 'Modified Date'} # Fields to display
        context['fields'] = fields
        # context['fields'] = [field.name for field in self.model._meta.get_fields()]
        return context


# within ldap
'''
class DepartemenListView(ListView):
    model = Departemen
    template_name = 'DMSApp/CrudDepartemen/view.html'
    context_object_name = 'departemen_list'  # For ListView

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_dokumen'] = KategoriDokumen.objects.filter(is_active=True)
        fields = {'department': 'Department'} # Fields to display
        context['fields'] = fields
        # context['fields'] = [field.name for field in self.model._meta.get_fields()]
        return context
'''


class DepartemenUpdateView(UpdateView): # Show in modal
    model = Departemen
    fields = []
    
    def post(self, request, pk):
        if self.request.user.is_superuser or self.request.user.is_releaser:
            department_instance_update = Departemen.objects.get(id=pk)
            nma_departemen = request.POST.get('department')
            kode_departemen = request.POST.get('department_code')

            if kode_departemen:
                if Departemen.objects.filter(department_code=kode_departemen).exclude(id=pk).exists():
                    raise PermissionDenied("Cannot update this code department because instances exist.")
            
            # Check if there is an existing Department with the same name, excluding the current department
            if Departemen.objects.filter(department=nma_departemen).exclude(id=pk).exists():
                raise PermissionDenied("Cannot update this department because instances exist.")
            
            # Get the current department name
            current_department_name = department_instance_update.department

            # If no errors, update the department instance
            # Retrieve all possible keys
            possible_keys = ['department', 'department_code', 'company', 'address']

            # Iterate over all possible keys and update the instance
            for key in possible_keys:
                if key in request.POST:
                    setattr(department_instance_update, key, request.POST.get(key))

            department_instance_update.save()

            # Handle related documents
            selected_dokumen_ids = request.POST.getlist('checklist_dokumen')
            dokumen = KategoriDokumen.objects.filter(id__in=selected_dokumen_ids)
            department_instance_update.related_category.set(dokumen)
            # department_instance_update.related_category.add(*dokumen)

            # Rename the directory for each selected document
            for dok_id in selected_dokumen_ids:
                try:
                    dokumen_instance = KategoriDokumen.objects.get(id=dok_id)
                    old_folder_path = os.path.join(folder_target, dokumen_instance.document, current_department_name)
                    new_folder_path = os.path.join(folder_target, dokumen_instance.document, nma_departemen)
                    
                    if os.path.exists(old_folder_path):
                        os.rename(old_folder_path, new_folder_path)
                    else:
                        print(f"The directory '{old_folder_path}' does not exist.")
                except:
                    print(f"Dokumen with id {dok_id} does not exist.")

            return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            raise PermissionDenied("You do not have the necessary permissions.")
            

class DepartemenActivateDeactivateView(UpdateView): # Show in modal

    def post(self, request, pk):
        if self.request.user.is_superuser or self.request.user.is_releaser:
            department_instance_update = Departemen.objects.get(id=pk)
            opsi_aktivasi = request.POST.get('aktivasi')

            if opsi_aktivasi == "nonaktif":
                department_instance_update.is_active = False
                department_instance_update.save(update_fields=['is_active'])
            else:
                department_instance_update.is_active = True
                department_instance_update.save(update_fields=['is_active'])

            return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            raise PermissionDenied("You do not have the necessary permissions.")
    

class DepartemenDeleteView(DeleteView): # Show in modal

    def post(self, request, pk):
        if self.request.user.is_superuser or self.request.user.is_releaser:
            department_instance_delete = Departemen.objects.get(id=pk)

            # Check if there are related instances of Arsip with the same parent department
            if Arsip.objects.filter(parent_department=pk).exists():
                # If related Arsip instances exist, raise PermissionDenied
                raise PermissionDenied("Cannot delete this department because related Arsip instances exist.")
            
            # Check if there are related instances of Arsip with the same parent department
            if UserDetail.objects.filter(user_department=pk).exists():
                # If related Arsip instances exist, raise PermissionDenied
                raise PermissionDenied("Cannot delete this department because related UserDetail instances exist.")


            # Iterate over each relasi_departemen instance
            for relasi_departemen in department_instance_delete.related_category.all():
                # Construct the path to the directory
                path = os.path.join(folder_target, relasi_departemen.document, department_instance_delete.department)

                if os.path.exists(path):
                    os.rmdir(path)

            department_instance_delete.delete()

            return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            raise PermissionDenied("You do not have the necessary permissions.")
    

# Versi update u/ delete
'''
class DepartemenDeleteView(UpdateView):

    def post(self, request, pk):
        department_instance_delete = Departemen.objects.get(id=pk)

        # Check if there are related instances of Arsip with the same parent department
        if Arsip.objects.filter(parent_department=pk).exists():
            # If related Arsip instances exist, raise PermissionDenied
            raise PermissionDenied("Cannot delete this department because related Arsip instances exist.")

        # If no related Arsip instances exist, mark the department as deleted
        department_instance_delete.is_deleted = True
        department_instance_delete.save(update_fields=['is_deleted'])

        return redirect(self.request.META.get('HTTP_REFERER'))
'''
    

class DokumenListView(CreateView, ListView): # CreateView show in modal
    model = KategoriDokumen
    template_name = 'DMSApp/CrudKategoriDokumen/view.html'
    context_object_name = 'dokumen_list'  # For ListView
    fields = ['document_initial', 'document']
    success_url = '/document/page/'

    def get_queryset(self):
        return KategoriDokumen.objects.order_by('document')

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
        if self.request.user.is_superuser or self.request.user.is_releaser:

            # Check for duplicates of document name and document initial
            if KategoriDokumen.objects.filter(document=form.cleaned_data['document']).exists():
                # Raise PermissionDenied if a duplicate department is found
                raise PermissionDenied("Cannot create this document because an instance with the same document already exists.")
            
            if KategoriDokumen.objects.filter(document_initial=form.cleaned_data['document_initial']).exists():
                raise PermissionDenied("Cannot create this document because an instance with the same document with this initial code already exists.")
            
            # If no duplicates, save kategori
            kategori = form.save()

            # Handle related labels
            selected_labels = self.request.POST.getlist('checklist_label')
            for label_name in selected_labels:
                # Get or create the KategoriDokumenLabel instance
                label, created = KategoriDokumenLabel.objects.get_or_create(label=label_name)
                # Add the label to the related_label field of the KategoriDokumen instance
                kategori.related_label.add(label)
        
            return super().form_valid(form)
        else:
            raise PermissionDenied("You do not have the necessary permissions.")
        

class DokumenUpdateView(UpdateView): # Show in modal
    model = KategoriDokumen
    fields = []

    def post(self, request, pk):
        if self.request.user.is_superuser or self.request.user.is_releaser:
            document_instance_update = KategoriDokumen.objects.get(id=pk)
            nma_dokumen = request.POST.get('document')
            init_dokumen = request.POST.get('document_initial')

            # Check if there is an existing Dokumen
            if KategoriDokumen.objects.filter(document=nma_dokumen).exclude(id=pk).exists():
                # Raise PermissionDenied if a duplicate department is found
                raise PermissionDenied("Cannot create this document because an instance with the same document already exists.")

            # Check if there is an existing initial dokumen
            if KategoriDokumen.objects.filter(document_initial=init_dokumen).exclude(id=pk).exists():
                raise PermissionDenied("Cannot create this document because an instance with the same document with this initial code already exists.")
            
            # Get the current name of the document
            current_document_name = document_instance_update.document            

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
                label, created = KategoriDokumenLabel.objects.get_or_create(name=nma_label)
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
        else:
            raise PermissionDenied("You do not have the necessary permissions.")
    '''
        old_folder_path = os.path.join(folder_target, current_document_name)
        new_folder_path = os.path.join(folder_target, nma_dokumen)
        os.rename(old_folder_path, new_folder_path)

        return redirect(self.request.META.get('HTTP_REFERER'))
    '''


class DokumenActivateDeactivateView(UpdateView): # Show in modal

    def post(self, request, pk):
        if self.request.user.is_superuser or self.request.user.is_releaser:
            menu_document_instance_update = KategoriDokumen.objects.get(id=pk)
            opsi_aktivasi = request.POST.get('aktivasi')

            if opsi_aktivasi == "nonaktif":
                menu_document_instance_update.is_active = False
                menu_document_instance_update.save(update_fields=['is_active'])
            else:
                menu_document_instance_update.is_active = True
                menu_document_instance_update.save(update_fields=['is_active'])

            return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            raise PermissionDenied("You do not have the necessary permissions.")
    
class DokumenDeleteView(DeleteView): # Show in modal

    def post(self, request, pk):
        if self.request.user.is_superuser or self.request.user.is_releaser:
            dokumen_instance_delete = KategoriDokumen.objects.get(id=pk)

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
        else:
            raise PermissionDenied("You do not have the necessary permissions.")
    

class ArsipListView(ListView):
    model = Departemen
    template_name = 'DMSApp/CrudArsip/view.html'
    context_object_name = 'departemen_list'

    def get_queryset(self):
        # Get the nama_dept from the request parameters
        nma_departemen = self.request.GET.get('dept')

        if nma_departemen:
            # Retrieve the Departemen object with the given department_id
            departemen = Departemen.objects.get(department=nma_departemen, is_active=True)
                
            # Retrieve the related MenuDokumen objects for the Departemen
            queryset = departemen.related_category.all().order_by('document')
            
        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nma_dokumen = self.request.GET.get('menu')
        nma_departemen = self.request.GET.get('dept')

        if nma_departemen:
            context['nm_departemen'] = nma_departemen
            if nma_dokumen:
                context['nm_dokumen'] = nma_dokumen
                context['data_dokumen_list'] = KategoriDokumen.objects.filter(document=nma_dokumen)
                nma_label = KategoriDokumen.objects.get(document=nma_dokumen)
                relasi_label = nma_label.related_label.all()
                context['nm_label'] = relasi_label

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
        # Get the values from the form
        nma_dokumen = self.request.POST.get('dokumen')
        nma_departemen = self.request.POST.get('departemen')
        nma_arsip = self.request.POST.get('document_name')
        no_arsip = self.request.POST.get('document_no')
        # no_form = self.request.POST.get('form_no')
        no_revisi = self.request.POST.get('revision_no')
        sub_dokumen_no = self.request.POST.get('sub_doc_no')
        
        # Retrieve IDs from the database based on the names
        dokumen_obj = KategoriDokumen.objects.get(document=nma_dokumen)
        departemen_obj = Departemen.objects.get(department=nma_departemen)

        if self.request.user.is_uploader and self.request.user.user_department == departemen_obj:
            
            # Check if a document name or document no with the same name already exists
            if Arsip.objects.filter(document_name=nma_arsip).exists() or Arsip.objects.filter(document_name=nma_arsip, document_no=no_arsip).exists():
                raise PermissionDenied('An entry with this document name or document number already exists.')
                            
            if sub_dokumen_no:
                # Check if a document name with sub document number or document no with sub document number already exists
                if Arsip.objects.filter(document_name=nma_arsip, sub_document_no=sub_dokumen_no).exists() or Arsip.objects.filter(document_no=no_arsip, sub_document_no=sub_dokumen_no).exists():
                    raise PermissionDenied('An entry with this document name or document number already exists.')
                else:
                    form.instance.sub_document_no=sub_dokumen_no

            # Get the values revision
            nma_arsip = self.request.GET.get('archive')

            if nma_arsip:
                # Check if a document name and revision no with the same name already exists
                if Arsip.objects.filter(document_name=nma_arsip, revision_no=no_revisi).exists():
                    raise ValidationError('An entry with this revision number already exists.')

                

            '''
            elif no_arsip:
                # Check if a document name or document no with the same name already exists
                if Arsip.objects.filter(document_name=nma_arsip).exists() or Arsip.objects.filter(document_no=no_arsip).exists():
                    raise ValidationError('An entry with this document name or document number already exists.')
            '''

            '''
            elif no_form:
                # Check if a document name or form no with the same name already exists
                if Arsip.objects.filter(document_name=nma_arsip).exists() or Arsip.objects.filter(form_no=no_form).exists():
                    raise ValidationError('An entry with this document name or form number already exists.')
            '''
            
            # Set the IDs to the form instance before saving
            form.instance.parent_document = dokumen_obj
            form.instance.parent_department = departemen_obj

            # Save the form
            self.object = form.save()

            # Handle saving dynamic fields and files
            directory = os.path.join(folder_target, 'temp_directory', nma_dokumen, nma_departemen)
            # directory = os.path.join(folder_target, nma_dokumen, nma_departemen)
            
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

                            # Generate a new filename (you can use different logic to generate it)
                            original_filename, file_extension = os.path.splitext(file_value.name)
                            new_filename = 'new_name_for_file' + file_extension

                            # filename = fs.save(file_value.name, file_value)
                            filename = fs.save(new_filename, file_value)

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
        else:
            raise PermissionDenied("You do not have the necessary permissions.")
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nma_dokumen = self.request.GET.get('menu')
        nma_departemen = self.request.GET.get('dept')

        # get_context_data for revision
        nma_arsip = self.request.GET.get('archive')

        if nma_dokumen:
            # Retrieve the related MenuDokumen objects for the Departemen
            nma_label = KategoriDokumen.objects.get(document=nma_dokumen)
            relasi_label = nma_label.related_label.all()
            context['nm_dokumen'] = nma_dokumen

            # Calculate next penomeran_dokumen
            max_document_no = Arsip.objects.aggregate(Max('document_no'))
            if max_document_no['document_no__max'] is not None:
                current_max = int(max_document_no['document_no__max'])
                next_number = current_max + 1
            else:
                # If no documents exist yet
                next_number = 0

            # Format penomeran_dokumen with leading zeros (e.g., "00", "01", "02")
            formatted_penomeran_dokumen = str(next_number).zfill(2)

            # Add penomeran_dokumen to context
            context['penomeran_dokumen'] = formatted_penomeran_dokumen

            context['nm_departemen'] = nma_departemen
            context['nm_arsip'] = nma_arsip
            kode_arsip = Arsip.objects.filter(document_name=nma_arsip, is_active=True)
            for i in kode_arsip:
                context['kode_arsip'] = i.document_no +' REV. '+ i.revision_no

            
            # Note untuk sementara di disable dulu sampai semua dokumen sudah di upload semua
            # remove revision_no jika register. confirm. 25/06/2024
            
            '''
            if kode_arsip.exists():
                context['nm_label'] = relasi_label
            else:
                context['nm_label'] = relasi_label.exclude(name='revision_no')
            '''
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
        nma_label = KategoriDokumen.objects.get(document=nma_dokumen)
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
            nma_label = KategoriDokumen.objects.get(document=nma_dokumen)
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
            nma_label = KategoriDokumen.objects.get(document=nma_dokumen)
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


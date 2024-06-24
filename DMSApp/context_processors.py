from .models import UserDetail, Departemen  # Import your model

def navbar_context(request):
    # menu_list_dokumen = MenuDokumen.objects.all().order_by('document')  # Retrieve menu list data
    # return {'menu_list_dokumen': menu_list_dokumen}
    departemen_list = Departemen.objects.filter(is_active=True).order_by('department')  # Retrieve department list data
    superuser_exist = UserDetail.objects.filter(is_superuser=True, is_active=True)
        # Return multiple context data
    return {
        # 'menu_list_dokumen': menu_list_dokumen,
        'cp_departemen_list': departemen_list,
        'superuser_exist': superuser_exist,
    }



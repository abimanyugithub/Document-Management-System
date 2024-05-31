from .models import MenuDokumen, Departemen  # Import your model

def navbar_context(request):
    # menu_list_dokumen = MenuDokumen.objects.all().order_by('document')  # Retrieve menu list data
    # return {'menu_list_dokumen': menu_list_dokumen}
    departemen_list = Departemen.objects.all().order_by('department')  # Retrieve department list data
    return {'departemen_list': departemen_list}
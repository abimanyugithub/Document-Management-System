from .models import MenuDokumen  # Import your model

def navbar_context(request):
    menu_list_dokumen = MenuDokumen.objects.all().order_by('sub_directory')  # Retrieve menu list data
    return {'menu_list_dokumen': menu_list_dokumen}
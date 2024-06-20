from .models import Dokumen, Departemen  # Import your model

def navbar_context(request):
    # menu_list_dokumen = MenuDokumen.objects.all().order_by('document')  # Retrieve menu list data
    # return {'menu_list_dokumen': menu_list_dokumen}
    departemen_list = Departemen.objects.filter(is_active=True).order_by('department')  # Retrieve department list data
    return {'cp_departemen_list': departemen_list}

# create a context processor that adds the username and email to the template context
def user_info(request):
    if request.user.is_authenticated:
        return {
            'username': request.user.username,
            'email': request.user.email
        }
    return {}
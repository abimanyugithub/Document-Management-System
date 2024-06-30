from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Your URL patterns
    path('auth/login/',  views.LoginView.as_view(), name='masuk'),
    path('auth/logout/', views.LogoutView.as_view(), name='keluar'),
    # path('auth/logout/', LogoutView.as_view(), name='keluar'),
    # path('login/', LoginView.as_view(template_name='DMSApp/Komponen/login.html'), name='login'),
    path('', views.DashboardView.as_view(), name='dashboard_view'),

    path('account/page/', views.AkunListView.as_view(), name='akun_view'),
    path('account/update/<str:pk>/', views.AkunUpdateView.as_view(), name='akun_update'),
    path('account/register/', views.AkunRegisterView.as_view(), name='akun_regist_view'),
    path('acount/activation/<str:pk>/', views.AkunActivateDeactivateView.as_view(), name='akun_is_active'),
    path('account/delete/<str:pk>/', views.AkunDeleteView.as_view(), name='akun_is_delete'),

    path('department/page/', views.DepartemenListView.as_view(), name='departemen_view'),
    path('department/update/<str:pk>/', views.DepartemenUpdateView.as_view(), name='departemen_update'),
    path('department/activation/<str:pk>/', views.DepartemenActivateDeactivateView.as_view(), name='departemen_is_active'),
    path('department/delete/<str:pk>/', views.DepartemenDeleteView.as_view(), name='departemen_is_delete'),

    path('category/page/', views.KategoriDokumenListView.as_view(), name='kategori_dokumen_view'),
    path('category/update/<str:pk>/', views.KategoriDokumenUpdateView.as_view(), name='kategori_dokumen_update'),
    path('category/activation/<str:pk>/', views.KategoriDokumenActivateDeactivateView.as_view(), name='kategori_dokumen_is_active'),
    path('category/delete/<str:pk>/', views.KategoriDokumenDeleteView.as_view(), name='kategori_dokumen_is_delete'),

    path('document/view/', views.DokumenListView.as_view(), name='dokumen_view'),
    path('document/create/', views.DokumenCreateView.as_view(), name='dokumen_create'),
    path('document/list-view/', views.DokumenNumberListView.as_view(), name='dokumen_list_view'),
    path('document/update/<str:pk>/', views.DokumenUpdateView.as_view(), name='dokumen_update'),
    path('document/delete/<str:pk>/', views.DokumenDeleteView.as_view(), name='dokumen_is_delete'),
    path('document/detail/<str:pk>/', views.DokumenDetailView.as_view(), name='dokumen_detail'),
    path('document/update-status/<str:pk>/', views.DokumenUpdateStatusView.as_view(), name='dokumen_status_update'),
    path('document/activation/<str:pk>/', views.DokumenActivateDeactivateView.as_view(), name='dokumen_is_active')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Your URL patterns
    path('', views.DashboardView.as_view(), name='view_dash'),
    path('department/page/', views.DepartemenListView.as_view(), name='departemen_view'),
    path('department/update/<str:pk>/', views.DepartemenUpdateView.as_view(), name='departemen_update'),
    path('department/delete/<str:pk>/', views.DepartemenEnableDisableView.as_view(), name='departemen_is_active'),

    path('document/page/', views.DokumenListView.as_view(), name='dokumen_view'),
    path('document/update/<str:pk>/', views.DokumenUpdateView.as_view(), name='dokumen_update'),
    path('document/delete/<str:pk>/', views.DokumenEnableDisableView.as_view(), name='dokumen_is_active'),

    path('document/view/', views.MenuDokumenListView.as_view(), name='menu_dokumen_view'),
    path('archive/create/', views.ArchiveCreateView.as_view(), name='archive_create'),
    #path('document/update/<str:pk>/', views.DokumenUpdateView.as_view(), name='dokumen_update'),
    #path('document/delete/<str:pk>/', views.DokumenDeleteView.as_view(), name='dokumen_delete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
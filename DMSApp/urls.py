from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Your URL patterns
    path('', views.DashboardView.as_view(), name='view_dash'),
    path('departemen/page/', views.DepartemenListView.as_view(), name='departemen_view'),
    path('departemen/update/<str:pk>/', views.DepartemenUpdateView.as_view(), name='departemen_update'),
    path('departemen/delete/<str:pk>/', views.DepartemenEnableDisableView.as_view(), name='departemen_is_active'),
   # path('fms/sop-flow/', views.SOPFlowListView.as_view(), name='sop_flow_view'),
   # path('fms/sop-flow/dokumen/', views.DokumenListView.as_view(), name='list_view'),

    path('menu-dokumen/', views.add_menu, name='add-menu'),
    path('menu-dokumen/page/', views.MenuDokumenListView.as_view(), name='menu_dokumen_view'),
    path('menu-dokumen/update/<str:pk>/', views.MenuDokumenUpdateView.as_view(), name='menu_dokumen_update'),
    # path('add-menu/create/', views.CreateMenuDokumenView.as_view(), name='menu_dokumen_create'),

    path('document/page/', views.DokumenListView.as_view(), name='dokumen_view'),
    path('document/update/<str:pk>/', views.DokumenUpdateView.as_view(), name='dokumen_update'),
    path('document/delete/<str:pk>/', views.DokumenDeleteView.as_view(), name='dokumen_delete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
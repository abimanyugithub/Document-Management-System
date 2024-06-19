from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

urlpatterns = [
    # Your URL patterns
    # path('login/',  views.LoginView.as_view(), name='login'),
    path('login/', LoginView.as_view(template_name='DMSApp/Komponen/login.html'), name='login'),

    path('', views.DashboardView.as_view(), name='dashboard_view'),
    path('department/page/', views.DepartemenListView.as_view(), name='departemen_view'),
    path('department/update/<str:pk>/', views.DepartemenUpdateView.as_view(), name='departemen_update'),
    path('department/activation/<str:pk>/', views.DepartemenActivateDeactivateView.as_view(), name='departemen_is_active'),
    path('department/delete/<str:pk>/', views.DepartemenDeleteView.as_view(), name='departemen_is_delete'),

    path('document/page/', views.DokumenListView.as_view(), name='dokumen_view'),
    path('document/update/<str:pk>/', views.DokumenUpdateView.as_view(), name='dokumen_update'),
    path('document/activation/<str:pk>/', views.DokumenActivateDeactivateView.as_view(), name='dokumen_is_active'),
    path('document/delete/<str:pk>/', views.DokumenDeleteView.as_view(), name='dokumen_is_delete'),

    path('archive/view/', views.ArsipListView.as_view(), name='arsip_view'),
    path('archive/create/', views.ArsipCreateView.as_view(), name='arsip_create'),
    path('archive/update/<str:pk>/', views.ArsipUpdateView.as_view(), name='arsip_update'),
    path('archive/delete/<str:pk>/', views.ArsipDeleteView.as_view(), name='arsip_is_delete'),
    path('archive/detail/<str:pk>/', views.ArsipDetailView.as_view(), name='arsip_detail'),
    path('archive/detail-list/', views.ArsipDetailListView.as_view(), name='arsip_list_detail'),
    path('archive/update-status/<str:pk>/', views.ArchiveUpdateStatusView.as_view(), name='arsip_status_update'),
    path('archive/activation/<str:pk>/', views.ArsipActivateDeactivateView.as_view(), name='arsip_is_active'),
    
    #path('document/update/<str:pk>/', views.DokumenUpdateView.as_view(), name='dokumen_update'),
    #path('document/delete/<str:pk>/', views.DokumenDeleteView.as_view(), name='dokumen_delete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.DashboardView.as_view(), name='view_dash'),
    path('departemen/page/', views.DepartemenListView.as_view(), name='departemen_view'),
    path('departemen/update/<str:pk>/', views.DepartemenUpdateView.as_view(), name='departemen_update'),
    path('departemen/delete/<str:pk>/', views.DepartemenEnableDisableView.as_view(), name='departemen_is_active'),
   # path('fms/sop-flow/', views.SOPFlowListView.as_view(), name='sop_flow_view'),
   # path('fms/sop-flow/dokumen/', views.DokumenListView.as_view(), name='list_view'),

    path('add-menu/', views.add_menu, name='add-menu'),
    path('document', views.DokumenListView.as_view(), name='dokumen_view'),
] 
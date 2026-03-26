from django.urls import path
from . import views

app_name = 'assemblies'

urlpatterns = [
    path('', views.assembly_list, name='assembly_list'),
    path('<int:assembly_id>/', views.assembly_detail, name='assembly_detail'),
    path('<int:assembly_id>/audit/', views.assembly_audit_report, name='audit_report'),
]
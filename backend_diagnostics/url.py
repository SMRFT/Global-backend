from django.urls import path, include
from .views import admin_registration
from . import views 

urlpatterns = [
path('adminreg/', admin_registration, name='admin_registration'),
path('create_employee/', views.create_employee, name='create_employee'),
path('set_employee_password/', views.set_employee_password, name='set_employee_password/'),
path('data-entitlements/', views.get_data_entitlements, name='get_data_entitlements'),
path('get_data_departments/', views.get_data_departments, name='get_data_departments'),
path('get_data_designation/', views.get_data_designation, name='get_data_designation'),
path('get_data_primaryroles/', views.get_data_primaryroles, name='get_data_primaryroles'),
path('get_data_additinalroles_list', views.get_data_additinalroles_list, name='get_data_additinalroles_list'),
path('update_department/<str:department_code>/', views.update_department, name='update_department'),
path('update_designation/<str:designation_code>/', views.update_designation, name='update_designation'),
]
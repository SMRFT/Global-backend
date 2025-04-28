from django.urls import path, include
from .views import admin_registration
from . import views 

urlpatterns = [
path('adminreg/', admin_registration, name='admin_registration'),
path('create_employee/', views.create_employee, name='create_employee'),
path('set_employee_password/', views.set_employee_password, name='set_employee_password/'),
path('update_department/<str:department_code>/', views.update_department, name='update_department'),
path('update_designation/<str:designation_code>/', views.update_designation, name='update_designation'),

path('_b_a_c_k_e_n_d/Global/adminreg/', admin_registration, name='admin_registration'),
path('_b_a_c_k_e_n_d/Global/create_employee/', views.create_employee, name='create_employee'),
path('_b_a_c_k_e_n_d/Global/set_employee_password/', views.set_employee_password, name='set_employee_password/'),
path('_b_a_c_k_e_n_d/Global/data-entitlements/', views.get_data_entitlements, name='get_data_entitlements'),
path('_b_a_c_k_e_n_d/Global/get_data_departments/', views.get_data_departments, name='get_data_departments'),
path('_b_a_c_k_e_n_d/Global/get_data_designation/', views.get_data_designation, name='get_data_designation'),
path('_b_a_c_k_e_n_d/Global/getprimaryandadditionalrole/', views.getprimaryandadditionalrole, name='getprimaryandadditionalrole'),
path('_b_a_c_k_e_n_d/Global/update_department/<str:department_code>/', views.update_department, name='update_department'),
path('_b_a_c_k_e_n_d/Global/update_designation/<str:designation_code>/', views.update_designation, name='update_designation'),
]

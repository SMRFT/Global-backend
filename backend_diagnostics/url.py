from django.urls import path
from .views import admin_registration ,get_employee_by_id,update_employee,create_employee
from . import views 

urlpatterns = [

path('adminreg/', admin_registration, name='admin_registration'),
path('create_employee/', views.create_employee, name='create_employee'),
path('upload-gridfs/', views.upload_gridfs, name='upload_gridfs'),
path('download-gridfs/<str:file_id>/', views.download_gridfs, name='download_gridfs'),
path('set_employee_password/', views.set_employee_password, name='set_employee_password/'),
path('data-entitlements/', views.get_data_entitlements, name='get_data_entitlements'),
path('get_data_departments/', views.get_data_departments, name='get_data_departments'),
path('get_data_designation/', views.get_data_designation, name='get_data_designation'),
path('get_employees_with_labels/', views.get_employees_with_labels, name='get_data_primary_role'),
path('getprimaryandadditionalrole/', views.getprimaryandadditionalrole, name='getprimaryandadditionalrole'),
path('update_department/<str:department_code>/', views.update_department, name='update_department'),
path('update_designation/<str:designation_code>/', views.update_designation, name='update_designation'),
path("get_employee_by_id/<str:employee_id>/", get_employee_by_id),
path("update_employee/<str:employee_id>/", update_employee),
path('serve_file/<str:file_id>/', views.serve_file, name="serve_file"),  # Add this line for file serving



]

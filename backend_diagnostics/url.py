from django.urls import path
from .views import admin_registration ,get_employee_by_id,update_employee,create_employee
from . import views
from django.contrib.auth import views as auth_views 

urlpatterns = [

path('adminreg/', admin_registration, name='admin_registration'),
path('create_employee/', views.create_employee, name='create_employee'),
path('upload-gridfs/', views.upload_gridfs, name='upload_gridfs'),
path('set_employee_password/', views.set_employee_password, name='set_employee_password/'),
path('data-entitlements/', views.get_data_entitlements, name='get_data_entitlements'),
path('get_data_departments/', views.get_data_departments, name='get_data_departments'),
path('get_data_designation/', views.get_data_designation, name='get_data_designation'),
path('get_employees_with_labels/', views.get_employees_with_labels, name='get_data_primary_role'),
path('getprimaryandadditionalrole/', views.getprimaryandadditionalrole, name='getprimaryandadditionalrole'),
 # Department
path("get_next_department_code/", views.get_next_department_code, name="get_next_department_code"),
path('update_department/<str:department_code>/', views.update_department, name='update_department'),
path('addnew_department/', views.addnew_department, name='add_newdepartment'),
path('addnew_designation/', views.addnew_designation, name='add_newdepartment'),

path("deactivate-user/<str:employeeId>/", views.DeactivateUserByEmployeeId),

# Designation
path("get_next_designation_code/", views.get_next_designation_code, name="get_next_designation_code"),
path('update_designation/<str:designation_code>/', views.update_designation, name='update_designation'),

path("get_employee_by_id/<str:employee_id>/", get_employee_by_id),
path("update_employee/<str:employee_id>/", update_employee),
path('serve_file/<str:file_id>/', views.serve_file, name="serve_file"),  
path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
path('reset-password/', views.reset_password, name='reset_password'),
path('validate-reset-token/', views.validate_reset_token, name='validate_reset_token'),
path('resend_employee_email/<str:employee_id>/', views.resend_employee_email, name='resend_employee_email'),
path('employees_birthdays_today/', views.get_todays_birthdays, name='employee-birthdays-today'),

]

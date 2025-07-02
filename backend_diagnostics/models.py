

from django.db import models
from django.contrib.auth.hashers import make_password
from bson import ObjectId





class ObjectIdField(models.Field):
    """ Custom field to store ObjectId """
    def __init__(self, *args, **kwargs):
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value) if isinstance(value, ObjectId) else value

    def from_db_value(self, value, expression, connection):
        return ObjectId(value) if value else None

class Admin_groups(models.Model): 
    email = models.EmailField(max_length=500, unique=True)
    employee_name = models.CharField(max_length=500)
    password = models.CharField(max_length=500)
    role = models.CharField(max_length=100)
    mobile = models.CharField(max_length=100, blank=True, null=True)
    id = ObjectIdField(primary_key=True, default=ObjectId)
    
    username = None  # Remove username field as we use email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        """Ensure password is hashed before saving"""
        if not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


from django.db import models
from django.utils.timezone import now
# class Profile(models.Model):
#     # Basic Information
#     employeeId = models.CharField(max_length=50, unique=True)
#     profileImage = models.CharField(max_length=1000, blank=True, null=True)  # GridFS file ID
#     employeeName = models.CharField(max_length=100)
#     fatherName = models.CharField(max_length=100, blank=True, null=True)
#     motherName = models.CharField(max_length=100, blank=True, null=True)
#     gender = models.CharField(max_length=10)
#     mobileNumber = models.CharField(max_length=15)
#     bloodGroup = models.CharField(max_length=5, blank=True, null=True)
#     maritalStatus = models.CharField(max_length=20, blank=True, null=True)
#     guardianNumber = models.CharField(max_length=150, blank=True, null=True)
#     dateOfBirth = models.DateField(blank=True, null=True)
#     email = models.EmailField(unique=True)
#     department = models.CharField(max_length=100)
#     designation = models.CharField(max_length=100)
#     primaryRole = models.CharField(max_length=150, blank=True, null=True)
#     additionalRoles = models.JSONField(default=list, blank=True, null=True)
#     dataEntitlements = models.JSONField(default=list, blank=True, null=True)

#     # File IDs for GridFS (All file uploads stored as GridFS file IDs)
#     aadhaarFileId = models.CharField(max_length=100, blank=True, null=True)
#     panFileId = models.CharField(max_length=100, blank=True, null=True)
#     fatherAadhaarFileId = models.CharField(max_length=100, blank=True, null=True)
#     motherAadhaarFileId = models.CharField(max_length=100, blank=True, null=True)
#     spouseAadhaarFileId = models.CharField(max_length=100, blank=True, null=True)
    
#     # Bank Details
#     bankDetails = models.JSONField(default=dict)

#     # Qualifications (List of dictionaries with file IDs)
#     qualifications = models.JSONField(default=list)

#     # Experience (List of dictionaries with file IDs)
#     experiences = models.JSONField(default=list)

#     # Audit fields
#     created_date = models.DateTimeField(default=lambda: now().astimezone(IST))
#     created_by = models.CharField(max_length=100, default='system')
#     lastmodified_by = models.CharField(max_length=100, default='system')
#     lastmodified_date = models.DateTimeField(default=lambda: now().astimezone(IST))

#     def __str__(self):
#         return self.employeeName
from djongo import models

class Profile(models.Model):
    employeeId = models.CharField(max_length=100, unique=True)
    employeeName = models.CharField(max_length=255)
    fatherName = models.CharField(max_length=255, null=True, blank=True)
    motherName = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=10)
    mobileNumber = models.CharField(max_length=15)
    bloodGroup = models.CharField(max_length=5, null=True, blank=True)
    maritalStatus = models.CharField(max_length=20, null=True, blank=True)
    guardianNumber = models.CharField(max_length=15, null=True, blank=True)
    dateOfBirth = models.DateField(null=True, blank=True)
    email = models.EmailField()

    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    primaryRole = models.CharField(max_length=100)
    additionalRoles = models.JSONField(default=list)
    dataEntitlements = models.JSONField(default=list)

    employmentStatus = models.CharField(max_length=20)
    registrationNumber = models.CharField(max_length=100, null=True, blank=True)
    validityDate = models.DateField(null=True, blank=True)

    kycDetails = models.JSONField(default=dict)
    familyDetails = models.JSONField(default=dict)
    qualifications = models.JSONField(default=list)
    experiences = models.JSONField(default=list)

    bankDetails = models.JSONField(default=dict)
    salaryDetails = models.JSONField(default=dict)
    fnfStatus = models.JSONField(default=dict)

    profileImage = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    # lastmodified_by = models.CharField(max_length=100)
    lastmodified_date = models.DateTimeField(auto_now=True)
    
    
    
    
class GridFSFile(models.Model):
    file_id = models.CharField(max_length=100, unique=True)
    filename = models.CharField(max_length=500)
    content_type = models.CharField(max_length=100)
    file_type = models.CharField(max_length=100)
    upload_date = models.DateTimeField(default=lambda: now().astimezone(IST))
    uploaded_by = models.CharField(max_length=100, default='system')
    
    def __str__(self):
        return f"{self.filename} ({self.file_id})"

    class Meta:
        db_table = 'gridfs_files'
        
        
        
from django.db import models
from django.utils.timezone import now
import pytz

IST = pytz.timezone('Asia/Kolkata')

class user(models.Model):
    employeeId = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)  # Sets is_active to True by default
    created_date = models.DateTimeField(default=lambda: now().astimezone(IST))  # Indian Timezone
    created_by = models.CharField(max_length=100, default='system')  # Default 'system'
    lastmodified_by = models.CharField(max_length=100, default='system')  # Default 'system'
    lastmodified_date = models.DateTimeField(default=lambda: now().astimezone(IST))  # Indian Timezone

    def __str__(self):
        return self.employeeId

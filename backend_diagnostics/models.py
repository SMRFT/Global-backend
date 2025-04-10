from dataclasses import fields
from pickle import TRUE
from unittest.util import _MAX_LENGTH
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone


from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.hashers import make_password
from bson import ObjectId

from django.utils.http import parse_http_date_safe



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

class Profile(models.Model):
    employeeId = models.CharField(max_length=50, unique=True)
    profileImage=models.CharField(max_length=1000,blank=True,null=True)
    employeeName = models.CharField(max_length=100)
    fatherName = models.CharField(max_length=100, blank=True, null=True)
    motherName = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10)
    mobileNumber = models.CharField(max_length=15)
    bloodGroup = models.CharField(max_length=5, blank=True, null=True)
    maritalStatus = models.CharField(max_length=20, blank=True, null=True)
    guardianNumber = models.CharField(max_length=150, blank=True, null=True)
    dateOfBirth  = models.DateField(blank=True, null=True)
    email = models.EmailField(unique=True)
    aadhaarNumber = models.CharField(max_length=12, unique=True)
    panNumber = models.CharField(max_length=10, unique=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    primaryRole= models.CharField(max_length=150, blank=True, null=True)
    additionalRoles = models.JSONField(default=list, blank=True, null=True)
    dataEntitlements = models.JSONField(default=list, blank=True, null=True)

    # Bank Details
    bankDetails = models.JSONField(default=dict)  # Example: {"bankName": "", "ifscCode": "", "accountNumber": "", "branch": ""}

    # Qualifications (List of dictionaries)
    qualifications = models.JSONField(default=list)  # Example: [{"degree": "", "institution": "", "passedOut": "", "percentage": ""}]

    # Experience (List of dictionaries)
    experiences = models.JSONField(default=list)  # Example: [{"company": "", "position": "", "yearsOfExperience": "", "fromDate": "", "toDate": "", "certificate": "", "certificateName": ""}]

    def __str__(self):
        return self.employeeName


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

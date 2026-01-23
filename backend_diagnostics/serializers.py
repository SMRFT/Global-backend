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
from backend_diagnostics.models import Admin_groups ,GridFSFile 
from datetime import date
from bson import ObjectId

class ObjectIdField(serializers.Field):
    def to_representation(self, value):
        return str(value)
    def to_internal_value(self, data):
        return ObjectId(data)
    
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_groups
        fields = ['id', 'employee_name', 'email', 'password', 'role', 'mobile']
        extra_kwargs = {
            'password': {'write_only': True}  # Password is not included in response
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Ensure password is hashed
        return super().create(validated_data)


from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from bson import ObjectId
from .models import  Admin_groups, GridFSFile, Profile
import ast
from collections import OrderedDict

class ObjectIdField(serializers.Field):
    def to_representation(self, value):
        return str(value)
    
    def to_internal_value(self, data):
        return ObjectId(data)

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_groups
        fields = ['id', 'employee_name', 'email', 'password', 'role', 'mobile']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class ProfileSerializer(serializers.ModelSerializer):
    qualifications = serializers.SerializerMethodField()
    experiences = serializers.SerializerMethodField()
    familyDetails = serializers.SerializerMethodField()
    kycDetails = serializers.SerializerMethodField()
    salaryDetails = serializers.SerializerMethodField()
    fnfStatus = serializers.SerializerMethodField()
    bankDetails = serializers.SerializerMethodField()
    signature = serializers.CharField(required=False, allow_null=True)
    
    class Meta:
        model = Profile
        fields = '__all__'

    def parse_field(self, field):
        if isinstance(field, str):
            try:
                return ast.literal_eval(field)
            except Exception:
                return field
        return field

    def get_qualifications(self, obj):
        return self.parse_field(obj.qualifications)

    def get_experiences(self, obj):
        return self.parse_field(obj.experiences)

    def get_familyDetails(self, obj):
        return self.parse_field(obj.familyDetails)

    def get_kycDetails(self, obj):
        return self.parse_field(obj.kycDetails)

    def get_salaryDetails(self, obj):
        return self.parse_field(obj.salaryDetails)

    def get_fnfStatus(self, obj):
        return self.parse_field(obj.fnfStatus)

    def get_bankDetails(self, obj):
        return self.parse_field(obj.bankDetails)

class GridFSFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GridFSFile
        fields = '__all__'

from pymongo import MongoClient
import os

client = MongoClient(os.getenv("GLOBAL_DB_HOST"))
db = client[os.getenv("GLOBAL_DB_NAME", "Global")]
dept_col = db["backend_diagnostics_Departments"]
desig_col = db["backend_diagnostics_Designation"]

class EmployeeBirthdaySerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "employeeId", "employeeName", "dateOfBirth", "age",
            "department", "designation"
        ]

    def get_department(self, obj):
        if not obj.department:
            return None
        dept = dept_col.find_one({"department_code": obj.department})
        return dept.get("department_name") if dept else None

    def get_designation(self, obj):
        if not obj.designation:
            return None
        desig = desig_col.find_one({"Designation_code": obj.designation})
        return desig.get("designation") if desig else None

from rest_framework import serializers
from .models import user

class userSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    class Meta:
        model = user
        fields = '__all__'

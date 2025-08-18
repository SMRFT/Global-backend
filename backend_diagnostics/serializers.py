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
from .models import Profile

from rest_framework import serializers
import ast
from collections import OrderedDict

class ProfileSerializer(serializers.ModelSerializer):
    qualifications = serializers.SerializerMethodField()
    experiences = serializers.SerializerMethodField()
    familyDetails = serializers.SerializerMethodField()
    kycDetails = serializers.SerializerMethodField()
    salaryDetails = serializers.SerializerMethodField()
    fnfStatus = serializers.SerializerMethodField()
    bankDetails = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = '__all__'

    def parse_field(self, field):
        if isinstance(field, str):
            try:
                # Try parsing stringified OrderedDict or list of OrderedDicts
                return ast.literal_eval(field)
            except Exception:
                return field  # fallback if already parsed
        return field  # already JSON or dict

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

    

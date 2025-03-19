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
from backend_diagnostics.models import Admin_groups  # ✅ ONLY IMPORT IT

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

class ProfileSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    class Meta:
        model = Profile
        fields = '__all__'


from rest_framework import serializers
from .models import user

class userSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    class Meta:
        model = user
        fields = '__all__'


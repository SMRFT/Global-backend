from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils import timezone
import base64
from django.conf import settings
from django.http import JsonResponse, HttpResponse,HttpResponseBadRequest,response
import secrets
import string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import os.path
import os
from django.views.decorators.csrf import csrf_exempt
from .models import Admin_groups
from .serializers import  AdminSerializer
from rest_framework import status
from .auth.auth import HasRoleAndDataPermission
from rest_framework.permissions import AllowAny
from rest_framework.response import Response  
from rest_framework.decorators import api_view
from .models import Profile
from .serializers import ProfileSerializer
from django.utils.timezone import now
import pytz
from .models import user
from .serializers import userSerializer
from django.contrib.auth.hashers import make_password
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from django.utils.decorators import method_decorator
import json
from datetime import datetime
load_dotenv()
IST = pytz.timezone('Asia/Kolkata')

# class AdminLogin(APIView):
#     def post(self, request):
#         cred = base64.b64decode(request.headers["Authorization"][6:]).decode('utf-8')
#         i = cred.index(':')
#         email = cred[:i]
#         password = cred[i+1:]
#         # Assuming you have an Admin model with email, password, name, role, and mobile fields
#         user = Admin.objects.filter(email=email).first()
#         if user is None:
#             raise AuthenticationFailed('User not found!')
#         if not user.check_password(password):
#             raise AuthenticationFailed('Incorrect password!')
#         if not user.is_active:
#             raise AuthenticationFailed('User is not active!')
#         # Generate a JWT token
#         refresh = RefreshToken.for_user(user)
#         refresh.access_token.set_exp(timezone.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])
#         access_token = str(refresh.access_token)
#         # Return the JWT token in 'Bearer' format
#         response_data = {
#             'jwt': f'Bearer {access_token}',  # JWT token in 'Bearer' format
#             'email': user.email,
#             'name': user.name,
#             'role': user.role,
#             'mobile': user.mobile
#         }
#         return Response(response_data)
    
@csrf_exempt
@api_view(['POST'])
@permission_classes([HasRoleAndDataPermission])
def admin_registration(request):
    """
    View for handling admin registration.
    """
    serializer = AdminSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # Fix response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
@permission_classes([HasRoleAndDataPermission])  # Use AllowAny if authentication is not required
def create_employee(request):
    if request.method == 'POST':
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Employee created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        employees = Profile.objects.all()
        serializer = ProfileSerializer(employees, many=True)
        return Response({"employees": serializer.data}, status=status.HTTP_200_OK)
   
@api_view(['POST', 'GET'])
@permission_classes([HasRoleAndDataPermission])
def set_employee_password(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['password'] = make_password(data['password'])  # Hash password securely
        data['is_active'] = True  # Ensures is_active is True
        data['created_date'] = now().astimezone(IST)  # Indian timezone
        data['lastmodified_date'] = now().astimezone(IST)
        data['created_by'] = data.get('created_by', 'system')  # Default to 'system'
        data['lastmodified_by'] = data.get('lastmodified_by', 'system')  # Default to 'system'

        serializer = userSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        users = user.objects.all()
        serializer = userSerializer(users, many=True)
        return Response({"employees": serializer.data}, status=status.HTTP_200_OK)

def get_data_entitlements(request):
    client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
    db = client[os.getenv('GLOBAL_DB_NAME')]
    collection = db['backend_diagnostics_DataEntitlements']

    # Extracting all fields excluding '_id'
    data_entitlements = collection.find({}, {'_id': 0})

    # Converting cursor to a list of dictionaries
    entitlements_list = list(data_entitlements)

    return JsonResponse({'dataEntitlements': entitlements_list})

def get_data_departments(request):
    client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
    db = client[os.getenv('GLOBAL_DB_NAME')]
    collection = db['backend_diagnostics_Departments']

    # Extracting all fields excluding '_id'
    data_departments = collection.find({}, {'_id': 0})

    # Converting cursor to a list of dictionaries
    departments_list = list(data_departments)

    return JsonResponse({'departments': departments_list})

def get_data_designation(request):
    client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
    db = client[os.getenv('GLOBAL_DB_NAME')]
    collection = db['backend_diagnostics_Designation']

    # Extracting all fields excluding '_id'
    data_designation = collection.find({}, {'_id': 0})

    # Converting cursor to a list of dictionaries
    designation_list = list(data_designation)

    return JsonResponse({'designations': designation_list})

# def get_data_primaryroles(request):
#     client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
#     db = client[os.getenv('GLOBAL_DB_NAME')]
#     collection = db['backend_diagnostics_RoleMapping']

#     # Extracting all fields excluding '_id'
#     data_primaryroles= collection.find({}, {'_id': 0})

#     # Converting cursor to a list of dictionaries
#     primaryroles_list = list(data_primaryroles)

#     return JsonResponse({'designations': primaryroles_list})


def getprimaryandadditionalrole(request):
    client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
    db = client[os.getenv('GLOBAL_DB_NAME')]
    collection = db['backend_diagnostics_RoleMapping']

    # Filter roles with is_active=True
    get_data = collection.find({"is_active": True}, {'_id': 0})

    # Convert cursor to list
    data_list = list(get_data)

    return JsonResponse({'designations': data_list})


client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
db = client[os.getenv('GLOBAL_DB_NAME')]

# Toggle Department Status
@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([HasRoleAndDataPermission])
def update_department(request, department_code):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            collection = db['backend_diagnostics_Departments']

            # Fetch the current department details
            department = collection.find_one({"department_code": department_code}, {"is_active": 1})

            if not department:
                return JsonResponse({"error": "Department not found"}, status=404)

            # Toggle status
            new_status = not department.get('is_active', False)
            current_time = datetime.utcnow().isoformat()

            # Update both created_date and lastmodified_date
            result = collection.update_one(
                {"department_code": department_code},
                {
                    "$set": {
                        "is_active": new_status,
                        "created_date": current_time,
                        "lastmodified_date": current_time
                    }
                }
            )

            if result.matched_count == 0:
                return JsonResponse({"error": "Failed to update department status"}, status=400)

            return JsonResponse({"message": "Department status updated successfully", "new_status": new_status}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# Toggle Designation Status
@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([HasRoleAndDataPermission])
def update_designation(request, designation_code):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            collection = db['backend_diagnostics_Designation']

            # Fetch the current designation details
            designation = collection.find_one({"Designation_code": designation_code}, {"is_active": 1})

            if not designation:
                return JsonResponse({"error": "Designation not found"}, status=404)

            # Toggle status
            new_status = not designation.get('is_active', False)
            current_time = datetime.utcnow().isoformat()

            # Update both created_date and lastmodified_date
            result = collection.update_one(
                {"Designation_code": designation_code},
                {
                    "$set": {
                        "is_active": new_status,
                        "created_date": current_time,
                        "lastmodified_date": current_time
                    }
                }
            )

            if result.matched_count == 0:
                return JsonResponse({"error": "Failed to update designation status"}, status=400)

            return JsonResponse({"message": "Designation status updated successfully", "new_status": new_status}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
import base64
from django.conf import settings
from django.http import JsonResponse
from django.http import JsonResponse, HttpResponse,HttpResponseBadRequest,response
import secrets
import string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import os.path
import os
# from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from .models import Admin_groups
from .serializers import  AdminSerializer
from rest_framework import status
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
    


from rest_framework.permissions import AllowAny

from rest_framework.response import Response  # Import Response

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])  # Use AllowAny if authentication is not required
def admin_registration(request):
    """
    View for handling admin registration.
    """
    serializer = AdminSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # Fix response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Profile
from .serializers import ProfileSerializer

@api_view(['POST', 'GET'])
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
    

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import user
from .serializers import userSerializer
from django.contrib.auth.hashers import make_password

@api_view(['POST', 'GET'])
def set_employee_password(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['password'] = make_password(data['password'])  # Hash password securely

        serializer = userSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        user = user.objects.all()
        serializer = userSerializer(user, many=True)
        return Response({"employees": serializer.data}, status=status.HTTP_200_OK)


from django.http import JsonResponse
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_data_entitlements(request):
    client = MongoClient(os.getenv('DB_HOST'))
    db = client[os.getenv('DB_NAME')]
    collection = db['backend_diagnostics_DataEntilements']

    # Extracting all fields excluding '_id'
    data_entitlements = collection.find({}, {'_id': 0})

    # Converting cursor to a list of dictionaries
    entitlements_list = list(data_entitlements)

    return JsonResponse({'dataEntitlements': entitlements_list})



from django.http import JsonResponse
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_data_departments(request):
    client = MongoClient(os.getenv('DB_HOST'))
    db = client[os.getenv('DB_NAME')]
    collection = db['backend_diagnostics_Departments']

    # Extracting all fields excluding '_id'
    data_departments = collection.find({}, {'_id': 0})

    # Converting cursor to a list of dictionaries
    departments_list = list(data_departments)

    return JsonResponse({'departments': departments_list})


from django.http import JsonResponse
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_data_designation(request):
    client = MongoClient(os.getenv('DB_HOST'))
    db = client[os.getenv('DB_NAME')]
    collection = db['backend_diagnostics_Designation']

    # Extracting all fields excluding '_id'
    data_designation = collection.find({}, {'_id': 0})

    # Converting cursor to a list of dictionaries
    designation_list = list(data_designation)

    return JsonResponse({'designations': designation_list})



#primaryroles get from the db
from django.http import JsonResponse
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_data_primaryroles(request):
    client = MongoClient(os.getenv('DB_HOST'))
    db = client[os.getenv('DB_NAME')]
    collection = db['backend_diagnostics_PrimaryRole']

    # Extracting all fields excluding '_id'
    data_primaryroles= collection.find({}, {'_id': 0})

    # Converting cursor to a list of dictionaries
    primaryroles_list = list(data_primaryroles)

    return JsonResponse({'designations': primaryroles_list})


#additinalroles get from the db
from django.http import JsonResponse
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_data_additinalroles_list(request):
    client = MongoClient(os.getenv('DB_HOST'))
    db = client[os.getenv('DB_NAME')]
    collection = db['backend_diagnostics_AdditionalRole']

    # Filter roles with is_active=True
    data_additinalroles = collection.find({"is_active": True}, {'_id': 0})

    # Convert cursor to list
    additinalroles_list = list(data_additinalroles)

    return JsonResponse({'designations': additinalroles_list})






#update codes

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('DB_HOST'))
db = client[os.getenv('DB_NAME')]

# Toggle Department Status
@method_decorator(csrf_exempt, name='dispatch')
def update_department(request, department_code):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)

            # Fetch current department status
            collection = db['backend_diagnostics_Departments']
            current_status = collection.find_one({"department_code": department_code}, {"is_active": 1})

            if not current_status:
                return JsonResponse({"error": "Department not found"}, status=404)

            # Toggle Status Logic
            new_status = not current_status.get('is_active', False)

            # Update Database
            result = collection.update_one(
                {"department_code": department_code},
                {"$set": {"is_active": new_status}}
            )

            if result.matched_count == 0:
                return JsonResponse({"error": "Failed to update department status"}, status=400)

            return JsonResponse({"message": "Department status updated successfully", "new_status": new_status}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# Toggle Designation Status
@method_decorator(csrf_exempt, name='dispatch')
def update_designation(request, designation_code):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)

            # Fetch current designation status
            collection = db['backend_diagnostics_Designation']
            current_status = collection.find_one({"Designation_code": designation_code}, {"is_active": 1})

            if not current_status:
                return JsonResponse({"error": "Designation not found"}, status=404)

            # Toggle Status Logic
            new_status = not current_status.get('is_active', False)

            # Update Database
            result = collection.update_one(
                {"Designation_code": designation_code},
                {"$set": {"is_active": new_status}}
            )

            if result.matched_count == 0:
                return JsonResponse({"error": "Failed to update designation status"}, status=400)

            return JsonResponse({"message": "Designation status updated successfully", "new_status": new_status}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)






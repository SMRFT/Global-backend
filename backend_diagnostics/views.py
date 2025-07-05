
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
import os
from django.views.decorators.csrf import csrf_exempt
from .serializers import  AdminSerializer
from rest_framework import status
from pyauth.auth import HasRoleAndDataPermission
from rest_framework.response import Response  
from rest_framework.decorators import api_view
from .models import Profile
from .serializers import ProfileSerializer
from django.utils.timezone import now
import pytz
from .models import user , GridFSFile
from .serializers import userSerializer
from django.contrib.auth.hashers import make_password
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from django.utils.decorators import method_decorator
import json
from datetime import datetime
import gridfs
import logging
from bson import ObjectId
from django.http import JsonResponse, HttpResponse
from django.http import JsonResponse,HttpResponse, Http404
from gridfs import GridFS
logger = logging.getLogger(__name__)
load_dotenv()
IST = pytz.timezone('Asia/Kolkata')


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

import json
import os
import gridfs
from datetime import datetime
from pymongo import MongoClient
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Profile
from .serializers import ProfileSerializer
import logging

logger = logging.getLogger(__name__)

import json

def safe_json_load(value):
    try:
        if isinstance(value, str):
            return json.loads(value)
        return value
    except Exception:
        return []


@api_view(['POST'])
def upload_gridfs(request):
    """Upload file to GridFS and return file ID"""
    client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
    db = client[os.getenv('GLOBAL_DB_NAME',"Global")]
    fs = gridfs.GridFS(db)
    
    if not fs:
        return Response({
            'error': 'GridFS not available'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        if 'file' not in request.FILES:
            return Response({
                'error': 'No file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        file_type = request.data.get('fileType', 'document')
        
        # Validate file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            return Response({
                'error': 'File size too large. Maximum 10MB allowed.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
        content_type = file.content_type
        
        if content_type not in allowed_types:
            return Response({
                'error': 'Invalid file type. Only JPEG, PNG, and PDF files are allowed.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.name}"
        
        # Upload to GridFS
        file_id = fs.put(
            file.read(),
            filename=filename,
            content_type=content_type,
            file_type=file_type,
            upload_date=datetime.now(),
            uploaded_by=request.user.username if request.user.is_authenticated else 'anonymous'
        )
        
        logger.info(f"File uploaded successfully: {filename} with ID: {file_id}")
        
        return Response({
            'fileId': str(file_id),
            'filename': filename,
            'contentType': content_type,
            'fileType': file_type
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error uploading file to GridFS: {str(e)}")
        return Response({
            'error': 'File upload failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import os
import json
import logging
import gridfs
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .models import Profile
from .serializers import ProfileSerializer


logger = logging.getLogger(__name__)

# Utility to safely parse JSON strings
def safe_json_load(value, default=None):
    if not value:
        return default if default is not None else []
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception as e:
        logger.warning(f"Invalid JSON input: {value} — {e}")
        return default if default is not None else []

# Upload file to GridFS inline
def upload_file_to_gridfs(file_obj, filename, content_type, file_type='document', uploaded_by='system'):
    try:
        client = MongoClient(os.getenv("GLOBAL_DB_HOST"))
        db = client[os.getenv("GLOBAL_DB_NAME","Global")]
        fs = gridfs.GridFS(db)

        file_id = fs.put(
            file_obj.read(),
            filename=filename,
            content_type=content_type,
            file_type=file_type,
            uploaded_by=uploaded_by,
            upload_date=datetime.utcnow()
        )

        return str(file_id)
    except Exception as e:
        raise Exception(f"GridFS upload failed: {str(e)}")

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
import logging, json
from .models import Profile
from .serializers import ProfileSerializer


logger = logging.getLogger(__name__)



@api_view(['POST'])
@permission_classes([HasRoleAndDataPermission])
def create_employee(request):
    try:
        data = request.data.copy()
        employee_id = data.get('auth-user-name') or data.get('employee_id', 'system')

        logger.info(f"Received employee data for ID: {data.get('employeeId')}")

        required_fields = ['employeeId', 'employeeName', 'email', 'gender', 'mobileNumber', 'dateOfBirth']
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            return Response({
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        profile, created = Profile.objects.get_or_create(employeeId=data.get('employeeId'))

        additional_roles = safe_json_load(data.get('additionalRoles'), [])
        data_entitlements = safe_json_load(data.get('dataEntitlements'), [])
        qualifications_data = safe_json_load(data.get('qualifications'), [])
        experiences_data = safe_json_load(data.get('experiences'), [])
        kids_details = safe_json_load(data.get('kidsDetails'), [])

        kyc_details = {
            'aadhaarNumber': data.get('kyc_aadhaarNumber'),
            'panNumber': data.get('kyc_panNumber'),
            'panType': data.get('kyc_panType')
        }

        family_details = {
            'fatherAadhaar': data.get('family_fatherAadhaar'),
            'fatherDob': data.get('family_fatherDob'),
            'motherAadhaar': data.get('family_motherAadhaar'),
            'motherDob': data.get('family_motherDob'),
            'spouseName': data.get('family_spouseName'),
            'spouseAadhaar': data.get('family_spouseAadhaar'),
            'spouseDob': data.get('family_spouseDob'),
            'kidsDetails': kids_details
        }

        bank_details = {
            'bankName': data.get('bank_bankName'),
            'ifscCode': data.get('bank_ifscCode'),
            'accountNumber': data.get('bank_accountNumber'),
            'branch': data.get('bank_branch')
        }

        salary_details = {
            'netSalary': data.get('salary_netSalary'),
            'grossSalary': data.get('salary_grossSalary'),
            'ctc': data.get('salary_ctc')
        }

        fnf_status = {
            'remarks': data.get('fnf_remarks')
        }

        profile.employeeName = data.get('employeeName')
        profile.fatherName = data.get('fatherName')
        profile.motherName = data.get('motherName')
        profile.gender = data.get('gender')
        profile.mobileNumber = data.get('mobileNumber')
        profile.bloodGroup = data.get('bloodGroup')
        profile.maritalStatus = data.get('maritalStatus')
        profile.guardianNumber = data.get('guardianNumber')
        profile.dateOfBirth = data.get('dateOfBirth')
        profile.email = data.get('email')
        profile.department = data.get('department')
        profile.designation = data.get('designation')
        profile.primaryRole = data.get('primaryRole')
        profile.additionalRoles = additional_roles
        profile.dataEntitlements = data_entitlements
        profile.employmentStatus = data.get('employmentStatus')
        profile.registrationNumber = data.get('registrationNumber')
        profile.validityDate = data.get('validityDate')
        profile.kycDetails = kyc_details
        profile.familyDetails = family_details
        profile.qualifications = qualifications_data
        profile.experiences = experiences_data
        profile.bankDetails = bank_details
        profile.salaryDetails = salary_details
        profile.fnfStatus = fnf_status
        profile.profileImage = data.get('profileImage')
        profile.created_by = employee_id

        profile.save()
        serializer = ProfileSerializer(profile)
        return Response({
            'success': True,
            'message': 'Employee profile created/updated successfully',
            'employee': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    except Exception as e:
        logger.exception("Employee creation/update failed")
        return Response({'success': False, 'error': str(e)}, status=500)


import ast



@api_view(['PUT'])
@permission_classes([HasRoleAndDataPermission])
def update_employee(request, employee_id):
    """Update employee profile with all frontend payload data"""
    
    try:
        # Get the existing profile
        try:
            profile = Profile.objects.get(employeeId=employee_id)
        except Profile.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Employee with ID {employee_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get the authenticated user ID
        updated_by = getattr(request.user, 'employee_id', request.user.username)
        
        # Extract all data from request
        data = request.data.copy()
        
        logger.info(f"Updating employee {employee_id} with data: {data}")
        
        # Parse JSON fields safely
        additional_roles = safe_json_load(data.get('additionalRoles', []))
        data_entitlements = safe_json_load(data.get('dataEntitlements', []))
        qualifications_data = safe_json_load(data.get('qualifications', []))
        experiences_data = safe_json_load(data.get('experiences', []))
        kids_details = safe_json_load(data.get('kidsDetails', []))
        
        # Prepare updated KYC details
        kyc_details = {
            'aadhaarNumber': data.get('kyc_aadhaarNumber', ''),
            'panNumber': data.get('kyc_panNumber', ''),
            'panType': data.get('kyc_panType', ''),
            'uanNumber': data.get('kyc_unaNumber', ''),
            'aadhaarFileId': data.get('aadhaarFileId'),
            'panFileId': data.get('panFileId'),
        }
        
        # Prepare updated family details
        family_details = {
            'fatherAadhaar': data.get('family_fatherAadhaar', ''),
            'fatherDob': data.get('family_fatherDob'),
            'fatherAadhaarFileId': data.get('fatherAadhaarFileId'),
            'motherAadhaar': data.get('family_motherAadhaar', ''),
            'motherDob': data.get('family_motherDob'),
            'motherAadhaarFileId': data.get('motherAadhaarFileId'),
            'spouseName': data.get('family_spouseName', ''),
            'spouseAadhaar': data.get('family_spouseAadhaar', ''),
            'spouseDob': data.get('family_spouseDob'),
            'spouseAadhaarFileId': data.get('spouseAadhaarFileId'),
            'kidsDetails': kids_details,
        }
        
        # Prepare updated bank details
        bank_details = {
            'bankName': data.get('bank_bankName', ''),
            'ifscCode': data.get('bank_ifscCode', ''),
            'accountNumber': data.get('bank_accountNumber', ''),
            'branch': data.get('bank_branch', ''),
        }
        
        # Prepare updated salary details
        salary_details = {
            'netSalary': data.get('salary_netSalary', ''),
            'grossSalary': data.get('salary_grossSalary', ''),
            'ctc': data.get('salary_ctc', ''),
        }
        
        # Prepare updated FNF status
        fnf_status = {
            'remarks': data.get('fnf_remarks', ''),
        }
        
        # Update profile fields
        profile.employeeName = data.get('employeeName', profile.employeeName)
        profile.fatherName = data.get('fatherName', profile.fatherName)
        profile.motherName = data.get('motherName', profile.motherName)
        profile.gender = data.get('gender', profile.gender)
        profile.mobileNumber = data.get('mobileNumber', profile.mobileNumber)
        profile.bloodGroup = data.get('bloodGroup', profile.bloodGroup)
        profile.maritalStatus = data.get('maritalStatus', profile.maritalStatus)
        profile.guardianNumber = data.get('guardianNumber', profile.guardianNumber)
        profile.dateOfBirth = data.get('dateOfBirth', profile.dateOfBirth)
        profile.email = data.get('email', profile.email)
        profile.department = data.get('department', profile.department)
        profile.designation = data.get('designation', profile.designation)
        profile.primaryRole = data.get('primaryRole', profile.primaryRole)
        profile.additionalRoles = additional_roles
        profile.dataEntitlements = data_entitlements
        profile.employmentStatus = data.get('employmentStatus', profile.employmentStatus)
        profile.registrationNumber = data.get('registrationNumber', profile.registrationNumber)
        profile.validityDate = data.get('validityDate', profile.validityDate)
        profile.created_by = updated_by  # Update who modified the profile
        
        # Update JSON fields
        profile.kycDetails = kyc_details
        profile.familyDetails = family_details
        profile.qualifications = qualifications_data
        profile.experiences = experiences_data
        profile.bankDetails = bank_details
        profile.salaryDetails = salary_details
        profile.fnfStatus = fnf_status
        
        # Update profile image if provided
        if data.get('profileImage'):
            profile.profileImage = data.get('profileImage')
        
        # Save the updated profile
        profile.save()
        
        logger.info(f"Successfully updated profile for employee: {profile.employeeId}")
        
        # Prepare response
        serializer = ProfileSerializer(profile)
        response_data = {
            'success': True,
            'message': 'Employee profile updated successfully',
            'employee': serializer.data,
            'updatedFields': list(data.keys())
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error updating employee {employee_id}: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to update employee profile',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




from rest_framework.response import Response
from rest_framework import status
from .models import Profile
from .serializers import ProfileSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([HasRoleAndDataPermission])
def get_employee_by_id(request, employee_id):
    try:
        profile = Profile.objects.filter(employeeId=employee_id).first()

        if not profile:
            return Response({"success": False, "message": "Employee not found."}, status=404)

        serializer = ProfileSerializer(profile)
        return Response({"success": True, "employee": serializer.data}, status=200)

    except Exception as e:
        logger.error(f"Error fetching employee by ID: {str(e)}")
        return Response({"success": False, "message": "Error retrieving employee."}, status=500)



@api_view(['GET'])
@permission_classes([HasRoleAndDataPermission])
def get_employees_with_labels(request):
    try:
        # Fetch employee profiles
        profiles = Profile.objects.all().order_by('-created_date')
        serializer = ProfileSerializer(profiles, many=True)
        employees = serializer.data

        # MongoDB setup
        client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
        db = client[os.getenv('GLOBAL_DB_NAME',"Global")]

        # Fetch all reference collections
        designations = {d['Designation_code']: d['designation'] for d in db['backend_diagnostics_Designation'].find({}, {'_id': 0})}
        departments = {d['department_code']: d['department_name'] for d in db['backend_diagnostics_Departments'].find({}, {'_id': 0})}
        entitlements = {d['DataEntitlementsCode']: d['DataEntitlements'] for d in db['backend_diagnostics_DataEntitlements'].find({}, {'_id': 0})}
        roles = {r['role_code']: r['role_name'] for r in db['backend_diagnostics_RoleMapping'].find({}, {'_id': 0})}

        # Match and enrich the employee data
        for emp in employees:
            emp['designation_name'] = designations.get(emp.get('designation'), 'N/A')
            emp['department_name'] = departments.get(emp.get('department'), 'N/A')
            emp['primary_role_name'] = roles.get(emp.get('primaryRole'), 'N/A')

            # Convert additionalRoles and dataEntitlements from stringified lists if needed
            import ast
            additional_roles = ast.literal_eval(emp.get('additionalRoles', '[]'))
            emp['additional_role_names'] = [roles.get(code, 'N/A') for code in additional_roles]

            entitlement_codes = ast.literal_eval(emp.get('dataEntitlements', '[]'))
            emp['data_entitlement_names'] = [entitlements.get(code, 'N/A') for code in entitlement_codes]

        return Response({'employees': employees}, status=200)

    except Exception as e:
        logger.error(f"Fetch error: {str(e)}")
        return Response({'error': 'Could not fetch enriched employee data'}, status=500)

import os
import mimetypes
@api_view(['GET'])
def serve_file(request, file_id):
    try:
        client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
        db = client[os.getenv('GLOBAL_DB_NAME','Global')]
        fs = GridFS(db)

        file_id = ObjectId(file_id)
        file = fs.get(file_id)

        # Try to detect MIME type from filename
        content_type, _ = mimetypes.guess_type(file.filename)
        if not content_type:
            content_type = file.content_type or 'application/octet-stream'  # fallback

        response = HttpResponse(file.read(), content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{file.filename}"'
        return response

    except Exception as e:
        raise Http404(f"File not found or invalid: {str(e)}")

    


@api_view(['POST', 'GET'])
@permission_classes([HasRoleAndDataPermission])
def set_employee_password(request):
    if request.method == 'POST':
        try:
            employee_id = request.data.get('auth-user-id')
            data = request.data.copy()

            if not data.get('password'):
                return Response(
                    {"success": False, "message": "Password is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Secure the password
            data['password'] = make_password(data['password'])

            # Audit fields
            current_time = now().astimezone(IST)
            data['is_active'] = True
            data['created_date'] = current_time
            data['lastmodified_date'] = current_time
            data['created_by'] = employee_id or 'system'
            data['lastmodified_by'] = employee_id or 'system'

            serializer = userSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Password created successfully.",
                        "data": serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )

            return Response(
                {"success": False, "message": "Validation error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"success": False, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    elif request.method == 'GET':
        users = user.objects.all()
        serializer = userSerializer(users, many=True)
        return Response(
            {"success": True, "employees": serializer.data},
            status=status.HTTP_200_OK
        )

    

@api_view(['POST', 'GET'])
@permission_classes([HasRoleAndDataPermission])
def get_data_entitlements(request):
    client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
    db = client[os.getenv('GLOBAL_DB_NAME',"Global")]
    collection = db['backend_diagnostics_DataEntitlements']

    # Extracting all fields excluding '_id'
    data_entitlements = collection.find({}, {'_id': 0})

    # Converting cursor to a list of dictionaries
    entitlements_list = list(data_entitlements)

    return JsonResponse({'dataEntitlements': entitlements_list})


@api_view(['POST', 'GET'])
@permission_classes([HasRoleAndDataPermission])
def get_data_departments(request):
    client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
    db = client[os.getenv('GLOBAL_DB_NAME','Global')]
    collection = db['backend_diagnostics_Departments']

    # Extracting all fields excluding '_id'
    data_departments = collection.find({}, {'_id': 0})

    # Converting cursor to a list of dictionaries
    departments_list = list(data_departments)

    return JsonResponse({'departments': departments_list})


@api_view(['POST', 'GET'])
@permission_classes([HasRoleAndDataPermission])
def get_data_designation(request):
    client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
    db = client[os.getenv('GLOBAL_DB_NAME','Global')]
    collection = db['backend_diagnostics_Designation']

    # Extracting all fields excluding '_id'
    data_designation = collection.find({}, {'_id': 0})

    # Converting cursor to a list of dictionaries
    designation_list = list(data_designation)

    return JsonResponse({'designations': designation_list})


@api_view(['POST', 'GET'])
@permission_classes([HasRoleAndDataPermission])
def getprimaryandadditionalrole(request):
    client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
    db = client[os.getenv('GLOBAL_DB_NAME','Global')]
    collection = db['backend_diagnostics_RoleMapping']

    # Filter roles with is_active=True
    get_data = collection.find({"is_active": True}, {'_id': 0})

    # Convert cursor to list
    data_list = list(get_data)

    return JsonResponse({'designations': data_list})




# Toggle Department Status
@api_view(['POST', 'GET', 'PUT'])
@permission_classes([HasRoleAndDataPermission]) 
def update_department(request, department_code):

    if request.method == 'PUT':
        try:
            client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
            db = client[os.getenv('GLOBAL_DB_NAME','Global')]
            collection = db['backend_diagnostics_Departments']

            # Get employee ID and other data from request.data
            data = request.data
            employee_id = data.get('auth-user-id') or data.get('employee_id', 'system')

            # Fetch the current department document
            department = collection.find_one({"department_code": department_code})

            if not department:
                return JsonResponse({"error": "Department not found"}, status=404)

            # Toggle the is_active field
            new_status = not department.get('is_active', False)

            # Prepare update fields
            current_time = datetime.utcnow().isoformat()
            update_data = {
                "is_active": new_status,
                "lastmodified_date": current_time,
                "lastmodified_by": employee_id,
            }

            if not department.get("created_date"):
                update_data["created_date"] = current_time
            if not department.get("created_by"):
                update_data["created_by"] = employee_id

            # Update in MongoDB
            result = collection.update_one(
                {"department_code": department_code},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return JsonResponse({"error": "Failed to update department status"}, status=400)

            return JsonResponse({
                "message": "Department status updated successfully",
                "new_status": new_status
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)





@api_view(['POST', 'GET', 'PUT'])
@permission_classes([HasRoleAndDataPermission])
def update_designation(request, designation_code):
    if request.method == 'PUT':
        try:
            # Use request.data ONLY (avoid request.body)
            data = request.data

            client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
            db = client[os.getenv('GLOBAL_DB_NAME','Global')]
            collection = db['backend_diagnostics_Designation']

            # Fetch the current designation details
            designation = collection.find_one(
                {"Designation_code": designation_code},
                {"is_active": 1, "created_date": 1, "created_by": 1}
            )

            if not designation:
                return JsonResponse({"error": "Designation not found"}, status=404)

            # Toggle status
            new_status = not designation.get('is_active', False)
            current_time = datetime.utcnow().isoformat()
            modifier_id = data.get('auth-user-id') or data.get('employee_id', 'system')

            update_data = {
                "is_active": new_status,
                "lastmodified_date": current_time,
                "lastmodified_by": modifier_id
            }

            # Optional fallback to ensure creation metadata
            if not designation.get("created_date"):
                update_data["created_date"] = current_time
            if not designation.get("created_by"):
                update_data["created_by"] = modifier_id

            # Update the designation
            result = collection.update_one(
                {"Designation_code": designation_code},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return JsonResponse({"error": "Failed to update designation status"}, status=400)

            return JsonResponse({
                "message": "Designation status updated successfully",
                "new_status": new_status
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

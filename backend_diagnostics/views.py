
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

def safe_json_load(val):
    if isinstance(val, str):
        return json.loads(val)
    return val

@api_view(['POST', 'GET'])
@permission_classes([HasRoleAndDataPermission]) 
def create_employee(request):
    """Create employee profile with integrated file uploads to GridFS"""

    def upload_file(file, filename_prefix=""):
        """Inline helper to upload file to GridFS and return file ID"""
        client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
        db = client[os.getenv('GLOBAL_DB_NAME')]
        fs = gridfs.GridFS(db)
        try:
            file_id = fs.put(
                file.read(),
                filename=f"{filename_prefix}_{file.name}" if filename_prefix else file.name,
                content_type=file.content_type
            )
            return str(file_id)
        except Exception as e:
            logger.error(f"GridFS upload error for {file.name}: {str(e)}")
            return None

    if request.method == 'POST':
        employee_id = request.data.get('auth-user-id')
        try:
            data = request.data
            files = request.FILES

            logger.info(f"Received employee data: {data}")
            logger.info(f"Received files: {list(files.keys())}")

            # Check for required fields
            required_fields = ['employeeId', 'employeeName', 'email', 'gender', 'mobileNumber']
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                return Response({'error': f"Missing fields: {', '.join(missing)}"}, status=400)

            file_ids = {}

            # Upload profile & KYC documents
            upload_map = {
                'profileImage': 'profile_image',
                'aadhaarFile': 'kyc_aadhaar',
                'panFile': 'kyc_pan',
                'fatherAadhaarFile': 'family_father_aadhaar',
                'motherAadhaarFile': 'family_mother_aadhaar',
                'spouseAadhaarFile': 'family_spouse_aadhaar'
            }
            for key, prefix in upload_map.items():
                if key in files:
                    fid = upload_file(files[key], prefix)
                    if fid:
                        file_ids[f'{key}Id'] = fid

            # Upload qualification certificates
            qualification_ids = {}
            for k, f in files.items():
                if k.startswith('qualificationCertificate_'):
                    qid = k.split('_')[1]
                    fid = upload_file(f, f'qualification_certificate_{qid}')
                    if fid:
                        qualification_ids[qid] = fid

            # Upload experience certificates
            experience_ids = {}
            for k, f in files.items():
                if k.startswith('experienceCertificate_'):
                    eid = k.split('_')[1]
                    fid = upload_file(f, f'experience_certificate_{eid}')
                    if fid:
                        experience_ids[eid] = fid

            # Upload kids' Aadhaar files
            kids_ids = {}
            for k, f in files.items():
                if k.startswith('kidsAadhaarFile_'):
                    kid_index = k.split('_')[1]
                    fid = upload_file(f, f'family_kid_{kid_index}_aadhaar')
                    if fid:
                        kids_ids[kid_index] = fid

            # Parse JSON fields
            qualifications = safe_json_load(data.get('qualifications', []))
            experiences = safe_json_load(data.get('experiences', []))
            kids = safe_json_load(data.get('kidsDetails', []))

            for q in qualifications:
                qid = str(q.get('id'))
                if qid in qualification_ids:
                    q['certificateFileId'] = qualification_ids[qid]

            for e in experiences:
                eid = str(e.get('id'))
                if eid in experience_ids:
                    e['certificateFileId'] = experience_ids[eid]

            for i, kid in enumerate(kids):
                if str(i) in kids_ids:
                    kid['aadhaarFileId'] = kids_ids[str(i)]

            # Final payload
            profile_data = {
                'employeeId': data.get('employeeId'),
                'employeeName': data.get('employeeName'),
                'fatherName': data.get('fatherName'),
                'motherName': data.get('motherName'),
                'gender': data.get('gender'),
                'mobileNumber': data.get('mobileNumber'),
                'bloodGroup': data.get('bloodGroup'),
                'maritalStatus': data.get('maritalStatus'),
                'guardianNumber': data.get('guardianNumber'),
                'dateOfBirth': data.get('dateOfBirth'),
                'email': data.get('email'),
                'department': data.get('department'),
                'designation': data.get('designation'),
                'primaryRole': data.get('primaryRole'),
                'additionalRoles': safe_json_load(data.get('additionalRoles', [])),
                'dataEntitlements': safe_json_load(data.get('dataEntitlements', [])),
                'employmentStatus': data.get('employmentStatus'),
                'registrationNumber': data.get('registrationNumber'),
                'validityDate': data.get('validityDate'),

                'kycDetails': {
                    'aadhaarNumber': data.get('kyc_aadhaarNumber'),
                    'aadhaarFileId': file_ids.get('aadhaarFileId'),
                    'panNumber': data.get('kyc_panNumber'),
                    'panFileId': file_ids.get('panFileId'),
                    'panType': data.get('kyc_panType'),
                },

                'familyDetails': {
                    'fatherAadhaar': data.get('family_fatherAadhaar'),
                    'fatherDob': data.get('family_fatherDob'),
                    'fatherAadhaarFileId': file_ids.get('fatherAadhaarFileId'),
                    'motherAadhaar': data.get('family_motherAadhaar'),
                    'motherDob': data.get('family_motherDob'),
                    'motherAadhaarFileId': file_ids.get('motherAadhaarFileId'),
                    'spouseName': data.get('family_spouseName'),
                    'spouseAadhaar': data.get('family_spouseAadhaar'),
                    'spouseDob': data.get('family_spouseDob'),
                    'spouseAadhaarFileId': file_ids.get('spouseAadhaarFileId'),
                    'kids': kids,
                },

                'qualifications': qualifications,
                'experiences': experiences,

                'bankDetails': {
                    'bankName': data.get('bank_bankName'),
                    'ifscCode': data.get('bank_ifscCode'),
                    'accountNumber': data.get('bank_accountNumber'),
                    'branch': data.get('bank_branch'),
                },

                'salaryDetails': {
                    'netSalary': data.get('salary_netSalary'),
                    'grossSalary': data.get('salary_grossSalary'),
                    'ctc': data.get('salary_ctc'),
                },

                'fnfStatus': {
                    'remarks': data.get('fnf_remarks')
                },

                'profileImage': file_ids.get('profileImageId'),
                'created_by': employee_id
            }


            serializer = ProfileSerializer(data=profile_data)
            if serializer.is_valid():
                profile = serializer.save()
                logger.info(f"Created profile for employeeId: {profile.employeeId}")
                return Response({
                    'message': 'Profile created',
                    'data': serializer.data,
                    'employeeId': profile.employeeId,
                    'uploadedFiles': {
                        'profileImage': bool(file_ids.get('profileImageId')),
                        'aadhaar': bool(file_ids.get('aadhaarFileId')),
                        'pan': bool(file_ids.get('panFileId')),
                        'qualificationCertificates': len(qualification_ids),
                        'experienceCertificates': len(experience_ids),
                        'familyDocuments': len([k for k in file_ids if 'family' in k.lower()])
                    }
                }, status=201)
            else:
                return Response({'error': 'Validation failed', 'details': serializer.errors}, status=400)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {str(e)}")
            return Response({'error': 'Invalid JSON in request'}, status=400)

        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}")
            return Response({'error': 'Server error', 'details': str(e)}, status=500)

    elif request.method == 'GET':
        try:
            profiles = Profile.objects.all().order_by('-created_date')
            serializer = ProfileSerializer(profiles, many=True)
            return Response({'employees': serializer.data}, status=200)
        except Exception as e:
            logger.error(f"Fetch error: {str(e)}")
            return Response({'error': 'Could not fetch employees'}, status=500)





@csrf_exempt
@api_view(['POST'])
def upload_gridfs(request):
    """Upload file to GridFS and return file ID"""
    client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
    db = client[os.getenv('GLOBAL_DB_NAME')]
    # collection = db['backend_diagnostics_Designation']
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
        
        # Save file metadata to database
        gridfs_file = GridFSFile.objects.create(
            file_id=str(file_id),
            filename=filename,
            content_type=content_type,
            file_type=file_type,
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
    
@api_view(['GET'])
def download_gridfs(request, file_id):
    """Download file from GridFS"""
    client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
    db = client[os.getenv('GLOBAL_DB_NAME')]
    # collection = db['backend_diagnostics_Designation']
    fs = gridfs.GridFS(db)
    if not fs:
        return Response({
            'error': 'GridFS not available'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        # Get file from GridFS
        grid_out = fs.get(ObjectId(file_id))
        
        # Create HTTP response
        response = HttpResponse(
            grid_out.read(),
            content_type=grid_out.content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{grid_out.filename}"'
        
        return response
        
    except gridfs.NoFile:
        return Response({
            'error': 'File not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error downloading file from GridFS: {str(e)}")
        return Response({
            'error': 'File download failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', 'GET'])
@permission_classes([HasRoleAndDataPermission])
def set_employee_password(request):
    if request.method == 'POST':
        employee_id = request.data.get('auth-user-id')
        data = request.data.copy()

        if not data.get('password'):
            return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Secure password hash
        data['password'] = make_password(data['password'])

        # Set audit fields
        data['is_active'] = True
        current_time = now().astimezone(IST)
        data['created_date'] = current_time
        data['lastmodified_date'] = current_time

        # Use employee_id if available, fallback to default 'system'
        data['created_by'] = employee_id or 'system'
        data['lastmodified_by'] = employee_id or 'system'

        serializer = userSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET request: fetch all users
    elif request.method == 'GET':
        users = user.objects.all()
        serializer = userSerializer(users, many=True)
        return Response({"employees": serializer.data}, status=status.HTTP_200_OK)
    

@api_view(['POST', 'GET'])
@permission_classes([HasRoleAndDataPermission])
def get_data_entitlements(request):
    client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
    db = client[os.getenv('GLOBAL_DB_NAME')]
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
    db = client[os.getenv('GLOBAL_DB_NAME')]
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
    db = client[os.getenv('GLOBAL_DB_NAME')]
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
@api_view(['POST', 'GET', 'PUT'])
@permission_classes([HasRoleAndDataPermission])
def update_department(request, department_code):


    if request.method == 'PUT':
        
        try:
            employee_id = request.data.get('auth-user-id')
            data = json.loads(request.body)
            collection = db['backend_diagnostics_Departments']

            # Fetch the current department details
            department = collection.find_one({"department_code": department_code})

            if not department:
                return JsonResponse({"error": "Department not found"}, status=404)

            # Toggle the is_active status
            new_status = not department.get('is_active', False)

            # Timestamp and user info
            current_time = datetime.utcnow().isoformat()
            modifier_id = request.data.get("employee_id") or "system"  # adjust key if named differently

            # Update the document
            update_data = {
                "is_active": new_status,
                "lastmodified_date": current_time,
                "lastmodified_by": modifier_id,
            }

            # Optionally set created_date/by if not present in DB
            if not department.get("created_date"):
                update_data["created_date"] = current_time
            if not department.get("created_by"):
                update_data["created_by"] = modifier_id

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




@api_view(['POST', 'GET','PUT'])
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
            employee_id = request.data.get('auth-user-id')
            # Update both created_date and lastmodified_date
            result = collection.update_one(
                {"Designation_code": designation_code},
                {
                    "$set": {
                        "is_active": new_status,
                        "created_date": current_time,
                        "lastmodified_date": current_time,
                        "lastmodified_by": data.get('employee_id', 'system')  
                    }
                }
            )

            if result.matched_count == 0:
                return JsonResponse({"error": "Failed to update designation status"}, status=400)

            return JsonResponse({"message": "Designation status updated successfully", "new_status": new_status}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
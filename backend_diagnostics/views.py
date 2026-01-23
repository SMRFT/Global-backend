
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
from .serializers import ProfileSerializer,EmployeeBirthdaySerializer
from django.utils.timezone import now
import pytz
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

from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from pymongo import MongoClient
import secrets
import string
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from pymongo import MongoClient
from django.conf import settings
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

# MongoDB connection
client = MongoClient(os.getenv('GLOBAL_DB_HOST'))
db = client[os.getenv('GLOBAL_DB_NAME',"Global")]
users_collection = db['backend_diagnostics_user']

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.utils.safestring import mark_safe
import json
from datetime import datetime
from bson.objectid import ObjectId
from django.contrib.auth.hashers import make_password

@csrf_exempt
def reset_password(request):
    """Render form on GET and handle password reset on POST"""
    if request.method == 'GET':
        # Get token from query param
        token = request.GET.get('token')
        if not token:
            return HttpResponse("<h3>Invalid or missing token</h3>")

        # Render HTML form with token injected into JavaScript
        template = loader.get_template('reset_password_form.html')
        context = {
            'token': mark_safe(f'"{token}"')  # token will be inserted as a JS string
        }
        return HttpResponse(template.render(context, request))

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            new_password = data.get('password')
            confirm_password = data.get('confirm_password')
            
            if not all([token, new_password, confirm_password]):
                return JsonResponse({
                    'error': 'Token, password, and confirm_password are required'
                }, status=400)
            
            if new_password != confirm_password:
                return JsonResponse({
                    'error': 'Passwords do not match'
                }, status=400)
            
            if len(new_password) < 8:
                return JsonResponse({
                    'error': 'Password must be at least 8 characters long'
                }, status=400)
            
            # Find user with valid reset token
            user = users_collection.find_one({
                'reset_token': token,
                'reset_token_expires': {'$gt': datetime.utcnow()}
            })
            
            if not user:
                return JsonResponse({
                    'error': 'Invalid or expired reset token'
                }, status=400)
            
            # Update user password and clear reset token
            users_collection.update_one(
                {'_id': user['_id']},
                {
                    '$set': {
                        'password': make_password(new_password),
                        'is_password_set': True,
                        'lastmodified_date': datetime.utcnow(),
                        'lastmodified_by':user['employeeId'],
                    },
                    '$unset': {
                        'reset_token': '',
                        'reset_token_expires': ''
                    }
                }
            )
            
            logger.info(f"Password reset successful for employee: {user['employeeId']}")
            
            return JsonResponse({
                'success': True,
                'message': 'Password reset successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def validate_reset_token(request):
    """Validate if reset token is still valid"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        token = data.get('token')
        
        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)
        
        # Find user with valid reset token
        user = users_collection.find_one({
            'reset_token': token,
            'reset_token_expires': {'$gt': datetime.utcnow()}
        })
        
        if not user:
            return JsonResponse({
                'valid': False,
                'error': 'Invalid or expired reset token'
            }, status=400)
        
        return JsonResponse({
            'valid': True,
            'employee_name': user['employee_name'],
            'email': user['email']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Token validation failed: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def generate_random_password(length=12):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_reset_token():
    """Generate a secure reset token"""
    return secrets.token_urlsafe(32)

def send_employee_welcome_email(employee_email, employee_name, reset_token):
    """Send welcome email with password reset link"""

    try:
        reset_url = f"{settings.FRONTEND_URL}reset-password?token={reset_token}"

        subject = "Welcome to Shanmuga Hospital Limited - Set Your Password"

        message = f"""
        Dear {employee_name},

        Welcome to Shanmuga Hospital Limited! Your employee Profile has been created successfully.

        To get started, please set your password by clicking the link below:
        {reset_url}

        This link will expire in 24 hours for security reasons.

        If you have any questions, please contact the HR department.

        Best regards,
        HR Team
        """

        html_message = f"""
        <html>
        <body>
            <h2>Welcome to Shanmuga Hospital Limited!</h2>
            <p>Dear {employee_name},</p>

            <p>Welcome to Shanmuga Hospital Limited! Your employee Profile has been created successfully.</p>

            <p>To get started, please set your password by clicking the button below:</p>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}"  
                   style="background-color: #007bff; color: white; padding: 12px 24px;  
                          text-decoration: none; border-radius: 5px; display: inline-block;"> 
                    Set Your Password 
                </a>
            </div>

            <p><strong>Note:</strong> This link will expire in 24 hours for security reasons.</p>

            <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
            <p><a href="{reset_url}">{reset_url}</a></p>

            <p>If you have any questions, please contact the HR department.</p>

            <p>Best regards,<br>HR Team<br>Shanmuga Hospital Limited</p>
        </body>
        </html>
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[employee_email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Welcome email sent successfully to {employee_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send welcome email to {employee_email}: {str(e)}")
        return False


def create_user_in_mongodb(employee_data):
    """Create user document in MongoDB users collection"""
    try:
        # Generate temporary password and reset token
        temp_password = generate_random_password()
        reset_token = generate_reset_token()
        
        # Create user document
        user_doc = {
            'employeeId': employee_data['employeeId'],
            'password': make_password(temp_password),  # Hash the password
            'is_active': True,
            'is_password_set': False,  # Flag to track if user has set their password
            'reset_token': reset_token,
            'reset_token_expires': datetime.utcnow() + timedelta(hours=24),
            'lastmodified_date': datetime.utcnow(),

        }
        
        # Check if user already exists
        existing_user = users_collection.find_one({'employee_id': employee_data['employeeId']})
        
        if existing_user:
            # Update existing user with new reset token
            users_collection.update_one(
                {'employee_id': employee_data['employeeId']},
                {
                    '$set': {
                        'email': employee_data['email'],
                        'reset_token': reset_token,
                        'reset_token_expires': datetime.utcnow() + timedelta(hours=24),
                        'lastmodified_date': datetime.utcnow(),
                    }
                }
            )
            logger.info(f"Updated existing user for employee ID: {employee_data['employeeId']}")
        else:
            # Insert new user
            result = users_collection.insert_one(user_doc)
            logger.info(f"Created new user for employee ID: {employee_data['employeeId']}, MongoDB ID: {result.inserted_id}")
        
        return reset_token
        
    except Exception as e:
        logger.error(f"Failed to create/update user in MongoDB: {str(e)}")
        raise

@api_view(['POST'])
@permission_classes([HasRoleAndDataPermission])
def create_employee(request):
    try:
        data = request.data.copy()
        employee_id = data.get('auth-user-id') or data.get('employee_id', 'system')
        logger.info(f"Received employee data for ID: {data.get('employeeId')}")
        
        required_fields = ['employeeId', 'employeeName', 'gender', 'mobileNumber', 'dateOfBirth']
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            return Response({
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        # Validate email format ONLY if email is provided
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError

        email = data.get('email')
        if email:  # ✅ validate only when available
            try:
                validate_email(email)
            except ValidationError:
                return Response({
                    'error': "Invalid email format"
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

        # Update profile fields
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
        profile.signatureFileId = data.get('signatureFileId') 
        profile.created_by = employee_id
        profile.save()

        # Create user in MongoDB and get reset token
        try:
            reset_token = create_user_in_mongodb(data)
            
            # Send welcome email with password reset link
            email_sent = send_employee_welcome_email(
                employee_email=data.get('email'),
                employee_name=data.get('employeeName'),
                reset_token=reset_token
            )
            
            if not email_sent:
                logger.warning(f"Employee created but email failed to send to {data.get('email')}")
                
        except Exception as e:
            logger.error(f"Failed to create user or send email: {str(e)}")
            # Continue with employee creation even if user creation/email fails
            # You might want to handle this differently based on your requirements

        serializer = ProfileSerializer(profile)
        
        response_data = {
            'success': True,
            'message': 'Employee profile created/updated successfully',
            'employee': serializer.data
        }
        
        # Add email status to response
        if 'email_sent' in locals():
            response_data['email_sent'] = email_sent
            if email_sent:
                response_data['message'] += ' and welcome email sent'
            else:
                response_data['message'] += ' but welcome email failed to send'
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    except Exception as e:
        logger.exception("Employee creation/update failed")
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([HasRoleAndDataPermission])
def resend_employee_email(request, employee_id):
    try:
        # Query Profile model with employeeId as a string
        employee = Profile.objects.get(employeeId=employee_id)
        
        # Fetch user from MongoDB users_collection
        user = users_collection.find_one({'employeeId': employee_id})
        if not user:
            return JsonResponse(
                {"success": False, "error": "User not found in authentication database"},
                status=404
            )
        
        # Generate a new reset token
        reset_token = secrets.token_urlsafe(32)
        users_collection.update_one(
            {'employeeId': employee_id},
            {
                '$set': {
                    'reset_token': reset_token,
                    'reset_token_expires': datetime.utcnow() + timedelta(hours=24),
                    'lastmodified_date': datetime.utcnow()
                }
            }
        )
        
        # Send welcome email with reset token
        success = send_employee_welcome_email(
            employee_email=employee.email,
            employee_name=employee.employeeName,
            reset_token=reset_token
        )
        if success:
            logger.info(f"Resent welcome email to {employee.email} for employee ID: {employee_id}")
            return JsonResponse(
                {"success": True, "message": "Email resent successfully"},
                status=200
            )
        else:
            logger.error(f"Failed to resend email to {employee.email}")
            return JsonResponse(
                {"success": False, "error": "Failed to resend email"},
                status=500
            )
    except Profile.DoesNotExist:
        logger.error(f"Employee with ID {employee_id} not found")
        return JsonResponse(
            {"success": False, "error": "Employee not found"},
            status=404
        )
    except Exception as e:
        logger.error(f"Error resending email for employee ID {employee_id}: {str(e)}")
        return JsonResponse(
            {"success": False, "error": f"Error resending email: {str(e)}"},
            status=500
        )
    
def parse_array_field(value):
    """Convert value into a list, supports JSON, comma-separated string, or list"""
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            # Try JSON decode first
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            # Fallback: split by comma
            return [v.strip() for v in value.split(",") if v.strip()]
    return []


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

        # Extract all data from request
        data = request.data.copy()
        lastmodified_by = data.get('auth-user-id')
        logger.info(f"Updating employee {employee_id} with data: {data}")
        
        # Parse JSON fields safely
# Parse roles and entitlements
        additional_roles = parse_array_field(data.get('additionalRoles'))
        data_entitlements = parse_array_field(data.get('dataEntitlements'))
        qualifications_data = parse_array_field(data.get('qualifications'))
        experiences_data = parse_array_field(data.get('experiences'))
        kids_details = parse_array_field(data.get('kidsDetails'))

        
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
        profile.lastmodified_by = lastmodified_by  # Update who modified the profile
        
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
        # Update signature if provided
        if data.get('signatureFileId'):
            profile.signatureFileId = data.get('signatureFileId')

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

@api_view(['DELETE'])
# @permission_classes([HasRoleAndDataPermission])
def delete_gridfs_file(request, file_id):
    try:
        client = MongoClient(os.getenv("GLOBAL_DB_HOST"))
        db = client[os.getenv("GLOBAL_DB_NAME", "Global")]
        fs = gridfs.GridFS(db)

        fs.delete(ObjectId(file_id))

        return Response({"success": True, "message": "File deleted successfully"})
    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

from django.http import HttpResponse
from bson import ObjectId
import mimetypes

@api_view(['GET'])
def download_gridfs(request, file_id):
    try:
        client = MongoClient(os.getenv("GLOBAL_DB_HOST"))
        db = client[os.getenv("GLOBAL_DB_NAME", "Global")]
        fs = gridfs.GridFS(db)

        file = fs.get(ObjectId(file_id))

        response = HttpResponse(file.read(), content_type=file.content_type)
        response['Content-Disposition'] = f'inline; filename="{file.filename}"'
        return response

    except Exception as e:
        return Response(
            {"success": False, "error": "File not found", "details": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )

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
        db = client[os.getenv('GLOBAL_DB_NAME', "Global")]
        users_collection = db['backend_diagnostics_user']

        # Fetch all reference collections
        designations = {d['Designation_code']: d['designation'] for d in db['backend_diagnostics_Designation'].find({}, {'_id': 0})}
        departments = {d['department_code']: d['department_name'] for d in db['backend_diagnostics_Departments'].find({}, {'_id': 0})}
        entitlements = {d['DataEntitlementsCode']: d['DataEntitlements'] for d in db['backend_diagnostics_DataEntitlements'].find({}, {'_id': 0})}
        roles = {r['role_code']: r['role_name'] for r in db['backend_diagnostics_RoleMapping'].find({}, {'_id': 0})}

        # ✅ Fetch both is_active and is_password_set in ONE query
        user_data = {
            user['employeeId']: {
                'is_active': user.get('is_active', True),
                'is_password_set': user.get('is_password_set', False)
            }
            for user in users_collection.find(
                {},
                {'employeeId': 1, 'is_active': 1, 'is_password_set': 1, '_id': 0}
            )
        }

        # Match and enrich the employee data
        for emp in employees:
            emp['designation_name'] = designations.get(emp.get('designation'), 'N/A')
            emp['department_name'] = departments.get(emp.get('department'), 'N/A')
            emp['primary_role_name'] = roles.get(emp.get('primaryRole'), 'N/A')

            import ast
            additional_roles = ast.literal_eval(emp.get('additionalRoles', '[]'))
            emp['additional_role_names'] = [roles.get(code, 'N/A') for code in additional_roles]

            entitlement_codes = ast.literal_eval(emp.get('dataEntitlements', '[]'))
            emp['data_entitlement_names'] = [entitlements.get(code, 'N/A') for code in entitlement_codes]

            # ✅ Add both values safely
            user_info = user_data.get(emp.get('employeeId'), {})
            emp['is_active'] = user_info.get('is_active', True)
            emp['is_password_set'] = user_info.get('is_password_set', False)

        return Response({'employees': employees}, status=200)

    except Exception as e:
        logger.error(f"Fetch error: {str(e)}")
        return Response({'error': 'Could not fetch enriched employee data'}, status=500)

import os, re
import mimetypes
from datetime import datetime

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

    


# @api_view(['POST', 'GET'])
# @permission_classes([HasRoleAndDataPermission])
# def set_employee_password(request):
#     if request.method == 'POST':
#         try:
#             employee_id = request.data.get('auth-user-id')
#             data = request.data.copy()

#             if not data.get('password'):
#                 return Response(
#                     {"success": False, "message": "Password is required."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # Secure the password
#             data['password'] = make_password(data['password'])

#             # Audit fields
#             current_time = now().astimezone(IST)
#             data['is_active'] = True
#             data['created_date'] = current_time
#             data['lastmodified_date'] = current_time
#             data['created_by'] = employee_id or 'system'
#             data['lastmodified_by'] = employee_id or 'system'

#             serializer = userSerializer(data=data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(
#                     {
#                         "success": True,
#                         "message": "Password created successfully.",
#                         "data": serializer.data
#                     },
#                     status=status.HTTP_201_CREATED
#                 )

#             return Response(
#                 {"success": False, "message": "Validation error", "errors": serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         except Exception as e:
#             return Response(
#                 {"success": False, "message": f"Server error: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     elif request.method == 'GET':
#         users = user.objects.all()
#         serializer = userSerializer(users, many=True)
#         return Response(
#             {"success": True, "employees": serializer.data},
#             status=status.HTTP_200_OK
#         )

    

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
# Helper function to generate next code
MONGO_URI = os.getenv("GLOBAL_DB_HOST",)
client = MongoClient(MONGO_URI)
db = client["Global"]  # replace with actual DB name
departments_col = db["backend_diagnostics_Departments"]

departments_col = db["backend_diagnostics_Departments"]
designations_col = db["backend_diagnostics_Designation"]

def _generate_next_code(collection, prefix, field):
    """Helper to generate next code like DEPT003 or DESG005"""
    last_doc = collection.find_one(
        {field: {"$regex": f"^{prefix}"}},
        sort=[(field, -1)]
    )
    if last_doc and field in last_doc:
        match = re.search(rf"{prefix}(\d+)", last_doc[field])
        if match:
            number = int(match.group(1)) + 1
            return f"{prefix}{number:03d}"
    return f"{prefix}001"


# ---- DEPARTMENT ----
def get_next_department_code(request):
    try:
        next_code = _generate_next_code(departments_col, "DEPT", "department_code")
        return JsonResponse({"success": True, "data": {"department_code": next_code}})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
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

from bson import ObjectId

@csrf_exempt
@permission_classes([HasRoleAndDataPermission]) 
def addnew_department(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            department_code = data.get("department_code")
            department_name = data.get("department_name")
            description = data.get("description", department_name)
            created_by = data.get("created_by", "system")

            new_department = {
                "department_code": department_code,
                "department_name": department_name,
                "description": description,
                "is_active": True,
                "created_date": datetime.utcnow().isoformat(),
                "created_by": created_by,
                "lastmodified_by": created_by,
                "lastmodified_date": datetime.utcnow().isoformat(),
            }
            result = departments_col.insert_one(new_department)

            # Add the inserted ID as string
            new_department["_id"] = str(result.inserted_id)

            return JsonResponse({"success": True, "data": new_department})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)



# ---- DESIGNATION ----
def get_next_designation_code(request):
    try:
        next_code = _generate_next_code(designations_col, "DESIG", "Designation_code")
        return JsonResponse({"success": True, "data": {"Designation_code": next_code}})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@permission_classes([HasRoleAndDataPermission]) 
def addnew_designation(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            designation_code = data.get("Designation_code")
            designation_name = data.get("designation")
            description = data.get("description", designation_name)
            created_by = data.get("created_by", "system")

            new_designation = {
                "Designation_code": designation_code,
                "designation": designation_name,
                "description": description,
                "is_active": True,
                "created_date": datetime.utcnow().isoformat(),
                "created_by": created_by,
                "lastmodified_by": created_by,
                "lastmodified_date": datetime.utcnow().isoformat(),
            }
            result = designations_col.insert_one(new_designation)
            
            new_designation["_id"] = str(result.inserted_id)

            return JsonResponse({"success": True, "data": new_designation})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)
        
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
import logging
import pytz
from datetime import date

from pymongo import MongoClient
import os

from .models import Profile
from .serializers import EmployeeBirthdaySerializer

logger = logging.getLogger(__name__)
IST = pytz.timezone("Asia/Kolkata")

# MongoDB setup
client = MongoClient(os.getenv("GLOBAL_DB_HOST"))
db = client[os.getenv("GLOBAL_DB_NAME", "Global")]
dept_col = db["backend_diagnostics_Departments"]
desig_col = db["backend_diagnostics_Designation"]
role_col = db["backend_diagnostics_RoleMapping"]
user_col = db["backend_diagnostics_user"]


@api_view(['GET'])
@permission_classes([HasRoleAndDataPermission]) 
def get_todays_birthdays(request):
    try:
        today = timezone.now().astimezone(IST).date()

        # Fetch all profiles
        profiles = Profile.objects.all()

        filtered_profiles = []
        for profile in profiles:
            if profile.dateOfBirth and profile.dateOfBirth.month == today.month and profile.dateOfBirth.day == today.day:
                # calculate age
                profile.age = today.year - profile.dateOfBirth.year - (
                    (today.month, today.day) < (profile.dateOfBirth.month, profile.dateOfBirth.day)
                )
                profile.save(update_fields=["age"])
                filtered_profiles.append(profile)

        if not filtered_profiles:
            return Response({"success": False, "message": "No birthdays found today."}, status=200)

        serializer = EmployeeBirthdaySerializer(filtered_profiles, many=True)
        birthday_data = serializer.data

        # 🔹 Enrich department & designation from Mongo
        for profile in birthday_data:
            dept_code = profile.get("department")
            desig_code = profile.get("designation")

            # Department
            if dept_code:
                dept = dept_col.find_one({"department_code": dept_code})
                if dept:
                    profile["department"] = dept.get("department_name")
                else:
                    logger.warning(f"No department found for code {dept_code}")

            # Designation
            if desig_code:
                desig = desig_col.find_one({"Designation_code": desig_code})
                if desig:
                    profile["designation"] = desig.get("designation")
                else:
                    logger.warning(f"No designation found for code {desig_code}")

        return Response({
            "success": True,
            "count": len(filtered_profiles),
            "birthdays": birthday_data
        }, status=200)

    except Exception as e:
        logger.error(f"Error fetching today's birthdays: {str(e)}")
        return Response({"success": False, "message": "Error retrieving data."}, status=500)
    

from .serializers import userSerializer
from .models import user
from django.contrib.auth.hashers import identify_hasher
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework import status

@api_view(['PATCH'])
@permission_classes([HasRoleAndDataPermission])
def set_employee_password(request):
    auth_user_id = request.data.get('auth-user-id')
    employee_id = request.data.get("employeeId")
    password = request.data.get("password")

    if not employee_id or not password:
        return Response(
            {"error": "employeeId and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 🔍 Always update existing document
    user_obj = user.objects.filter(employeeId=employee_id).first()
    if not user_obj:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # 🔐 Hash only if needed
    try:
        identify_hasher(password)
    except ValueError:
        password = make_password(password)

    # 🔒 Direct field update (NO serializer = NO duplicates)
    user_obj.password = password
    user_obj.is_password_set = True
    user_obj.is_active = True
    user_obj.lastmodified_by = auth_user_id
    user_obj.lastmodified_date = now().astimezone(IST)

    user_obj.save()

    return Response(
        {"message": "Password updated successfully"},
        status=status.HTTP_200_OK
    )


    # elif request.method == 'GET':
    #     users = user.objects.all()
    #     serializer = userSerializer(users, many=True)
    #     return Response({"employees": serializer.data}, status=status.HTTP_200_OK)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from .models import user
from .serializers import userSerializer

@api_view(['PATCH'])
def UpdateUserStatusByEmployeeId(request, employeeId):
    try:
        user_obj = user.objects.get(employeeId=employeeId)
    except user.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    data = request.data

    # Expecting is_active from frontend
    is_active = data.get('is_active')

    if is_active is None:
        return Response(
            {"error": "is_active field is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Who modified
    modified_by = data.get('auth-user-id') or data.get('employee_id', 'system')

    # Update status
    user_obj.is_active = bool(is_active)
    user_obj.lastmodified_date = now()
    user_obj.lastmodified_by = modified_by
    user_obj.save()

    serializer = userSerializer(user_obj)

    return Response(
        {
            "message": "User activated successfully" if user_obj.is_active else "User deactivated successfully",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )

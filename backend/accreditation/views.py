from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
import csv
import io
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import openpyxl

# Import models [NEEDS TO BE CHANGED/DELETED]
from .models import (
    DataProcess,
    FacultyCI,
    ProgramCI,
    AssessValidity,
    AccredReport,
    AnnualReport,
    Faculty,
    CSVUpload
)


# Check if user is admin
def is_admin(user):
    """Check if a user has admin or superuser privileges through role"""
    if hasattr(user, 'profile'):
        return user.profile.role == 'admin' # replace with group check instead
    return user.is_superuser

# Redirect to login if not authenticated
def login_view(request):
    """
    Display and process the login page
    """
    # If user is already authenticated, redirect to home
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'bcit_accreditation/bcit_accred_login.html')

def login_user(request):
    """
    Login form post request using django authentication and hashing
    """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "bcit_accreditation/bcit_accred_login.html")
    return render(request, "bcit_accreditation/bcit_accred_login.html")

def register_view(request):
    """
    Display and process the register page
    """
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'bcit_accreditation/bcit_accred_register.html')

def register_user(request):
    """
    Register post request, handling logic and adding to database
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Handling both entered passwords
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'bcit_accreditation/bcit_accred_register.html')
        
        # Use django password validator
        try:
            # Uses all of django's password validators to check password
            validate_password(password1)
        except ValidationError as e:
            for error in e:
                messages.error(request, error)
            return render(request, "bcit_accreditation/bcit_accred_register.html")

        # Handling username already existing
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'bcit_accreditation/bcit_accred_register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'bcit_accreditation/bcit_accred_register.html')

        # Create user and save it in the database
        user = User.objects.create_user(username=username, email=email, password=password1)
        # Faculty.objects.create(user=user, last_uploaded=None) add this later back after migration
        user.save()
        login(request, user)
        return redirect('home')

    return render(request, 'bcit_accreditation/bcit_accred_register.html')

def logout_user(request):
    """
    Logout post request
    """
    logout(request)
    return redirect('login')


# ALL FOLLOWING VIEWS MUST HAVE LOGIN_REQUIRED DECORATOR

@login_required
def home_view(request):
    """
    Display the unified home page (requires authentication)
    """
    # Simple context - no additional data needed for the card-based homepage
    context = {}
    
    return render(request, 'bcit_accreditation/bcit_accred_home.html', context)

@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """
    Display the admin dashboard (admin only)
    """
    # Get all users except the current admin
    users = User.objects.exclude(id=request.user.id).order_by('username')
    
    # For each user, get their last upload date
    for user in users:
        try:
            
            # Assuming we have a model that tracks uploads with a user foreign key and a date field
            last_upload = CSVUpload.objects.filter(user=user).order_by('-upload_date').first()
            if last_upload:
                user.last_upload = last_upload.upload_date.strftime('%Y-%m-%d')
            else:
                user.last_upload = None
        except Exception:
            user.last_upload = None
    
    context = {
        'users': users,
        'total_courses': None,
        'total_departments': None,
        'pending_updates': None,
        'required_actions': None,
        'recent_uploads': None,
        'recent_courses': None
    }
    return render(request, 'bcit_accreditation/bcit_accred_admin.html', context)

@login_required
def csv_upload_view(request):
    """
    Handle CSV or XLSX file upload and extract student data.
    """
    if request.method == 'POST' and request.FILES.get('csv_file'):
        uploaded_file = request.FILES['csv_file']
        file_name = uploaded_file.name.lower()

        try:
            # Convert uploaded file to rows: list of lists
            if file_name.endswith('.csv'):
                file_content = uploaded_file.read().decode('utf-8')
                csvfile = io.StringIO(file_content)
                rows = list(csv.reader(csvfile))

            elif file_name.endswith('.xlsx'):
                wb = openpyxl.load_workbook(uploaded_file, data_only=True)
                sheet = wb.active
                csv_buffer = io.StringIO()
                csv_writer = csv.writer(csv_buffer)
                for row in sheet.iter_rows(values_only=True):
                    csv_writer.writerow(row)
                csv_buffer.seek(0)
                rows = list(csv.reader(csv_buffer))

            else:
                return JsonResponse({'success': False, 'message': 'Unsupported file type. Please upload a .csv or .xlsx file.'})

            # Extract data starting from row 4 (index 3)
            extracted_data = []

            for row in rows[3:]:
                try:
                    student_id = row[1].strip() if row[1] else None
                    gai_score_raw = str(row[2]).strip() if row[2] else None

                    if student_id and len(student_id) == 9:
                        try:
                            gai_score = int(gai_score_raw)
                            extracted_data.append((student_id, gai_score))
                        except ValueError:
                            continue  # Skip rows with invalid GAI scores
                except IndexError:
                    continue  # Skip incomplete rows

            return JsonResponse({
                'success': True,
                'message': 'File uploaded and data extracted.',
                'file_name': uploaded_file.name,
                'file_size': uploaded_file.size,
                'extracted': extracted_data
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error processing file: {str(e)}'})

    return render(request, 'bcit_accreditation/csv_upload.html')

@login_required
def form_step1_view(request):
    """
    Display the first step of the form
    """
    return render(request, 'bcit_accreditation/bcit_accred_f1_course_and_ga.html')

@login_required
def form_step2_view(request):
    """
    Display the second step of the form
    """
    return render(request, 'bcit_accreditation/bcit_accred_f2_info_about_assessment.html')

@login_required
def form_step3_view(request):
    """
    Display the third step of the form (comments & confirmation)
    """
    return render(request, 'bcit_accreditation/bcit_accred_f3_comment_and_confirmation.html')

@login_required
def form_success_view(request):
    """
    Display the success page after form submission
    """
    return render(request, 'bcit_accreditation/bcit_accred_f4_successful_upload.html')

@login_required
def form_submit_view(request):
    """
    Process the form submission
    """
    if request.method == 'POST':
        try:
            # Here we put logic or function refrence to process the form data and save it to the database
            # For now, just return success
            return JsonResponse({
                'success': True,
                'message': 'Data saved successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error saving data: {str(e)}'
            })
    
    # If not POST, redirect to form step 1
    return redirect('form_step1')

# @login_required
# def analytics_view(request):
#     """
#     Display analytics dashboard
#     """
#     return render(request, 'bcit_accreditation/analytics.html')

@login_required
def analysis_view(request):
    """
    Display the new analytics/analysis dashboard with Tableau visualizations
    """
    return render(request, 'bcit_accreditation/bcit_accred_analysis.html')

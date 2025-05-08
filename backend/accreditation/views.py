from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
import csv
import io
from datetime import datetime

# Import models
from .models import (
    Department, 
    Program, 
    Course, 
    CSVUpload,
    LearningOutcome,
    GraduateAttribute,
    CourseGraduateAttribute,
    AssessmentMethod
)

# Check if user is admin
def is_admin(user):
    """Check if a user has admin privileges through staff status or role"""
    if hasattr(user, 'profile'):
        return user.is_staff or user.is_superuser or user.profile.role == 'admin'
    return user.is_staff or user.is_superuser

# Redirect to login if not authenticated
def login_view(request):
    """
    Display and process the login page
    """
    # If user is already authenticated, redirect to home
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'bcit_accreditation/bcit_accred_login.html')

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
    # Get counts for dashboard stats
    context = {
        'total_courses': Course.objects.count(),
        'total_departments': Department.objects.count(),
        'pending_updates': Course.objects.filter(accreditation_status='pending').count(),
        'required_actions': CSVUpload.objects.filter(status='failed').count() + CSVUpload.objects.filter(status='processing').count(),
        'recent_uploads': CSVUpload.objects.all()[:5],
        'recent_courses': Course.objects.all().order_by('-updated_at')[:5]
    }
    return render(request, 'bcit_accreditation/bcit_accred_admin.html', context)

@login_required
def course_details_view(request, course_id=None):
    """
    Display details for a specific course (requires authentication)
    """
    # Get course by ID or 404 if not found
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        
        # Get related data
        learning_outcomes = course.learning_outcomes.all().order_by('order')
        graduate_attributes = course.graduate_attributes.all().select_related('attribute')
        assessments = course.assessments.all()
        
        context = {
            'course': course,
            'learning_outcomes': learning_outcomes,
            'graduate_attributes': graduate_attributes,
            'assessments': assessments
        }
    else:
        # If no course_id, show a message and redirect to courses list
        messages.warning(request, "No course specified. Please select a course.")
        return redirect('courses')
    
    return render(request, 'bcit_accreditation/bcit_accred_course_details.html', context)

@login_required
def test_upload_view(request):
    """
    Handle CSV file upload test page (requires authentication)
    """
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        # Check if file is a CSV
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({'success': False, 'message': 'File is not a CSV'})
        
        try:
            # Access the file content - this will be where your colleague's function would be called
            file_content = csv_file.read()
            
            # Here, you would typically call your colleague's CSV processing function:
            # Example: result = your_colleagues_csv_function(file_content)
            
            # For testing that the file is properly uploaded and accessible
            row_count = file_content.decode('utf-8').count('\n')
            
            return JsonResponse({
                'success': True, 
                'message': f'File successfully uploaded! Found approximately {row_count} rows of data.',
                'file_name': csv_file.name,
                'file_size': csv_file.size
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error processing file: {str(e)}'
            })
    
    return render(request, 'bcit_accreditation/test.html')

@login_required
def csv_upload_view(request):
    """
    Handle production CSV file upload page (requires authentication)
    """
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        file_type = request.POST.get('file_type')
        
        # Check if file is a CSV
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({'success': False, 'message': 'File is not a CSV'})
        
        # Check if file type is provided
        if not file_type:
            return JsonResponse({'success': False, 'message': 'Data type not specified'})
        
        try:
            # Create CSV upload record
            upload = CSVUpload(
                user=request.user,
                file_name=csv_file.name,
                file_type=file_type,
                status='processing'
            )
            upload.save()
            
            # Process based on file_type - this would typically be handled by a background task
            # For demo, we'll just mark as successful
            upload.status = 'success'
            upload.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'File successfully uploaded as {file_type} data!'
            })
        except Exception as e:
            # Log error
            if 'upload' in locals():
                upload.status = 'failed'
                upload.error_message = str(e)
                upload.save()
            
            return JsonResponse({
                'success': False, 
                'message': f'Error processing file: {str(e)}'
            })
    
    # Get recent uploads for display in the template
    recent_uploads = CSVUpload.objects.filter(user=request.user).order_by('-upload_date')[:5]
    
    context = {
        'recent_uploads': recent_uploads
    }
    
    # Render the upload form
    return render(request, 'bcit_accreditation/csv_upload.html', context)

@login_required
def analytics_view(request):
    """
    Display the analytics dashboard with Tableau visualizations
    """
    # Get summary statistics for context
    context = {
        'total_courses': Course.objects.count(),
        'compliant_courses': Course.objects.filter(accreditation_status='compliant').count(),
        'partial_courses': Course.objects.filter(accreditation_status='partial').count(),
        'non_compliant_courses': Course.objects.filter(accreditation_status='non-compliant').count(),
        'pending_courses': Course.objects.filter(accreditation_status='pending').count(),
    }
    
    return render(request, 'bcit_accreditation/analytics.html', context)

@login_required
def courses_view(request):
    """
    Display the courses listing page with filtering and pagination
    """
    # Get all courses
    courses = Course.objects.all().select_related('department', 'program')
    
    # Handle search and filtering
    search_term = request.GET.get('search', '')
    department = request.GET.get('department', '')
    level = request.GET.get('level', '')
    status = request.GET.get('status', '')
    
    if search_term:
        courses = courses.filter(
            Q(code__icontains=search_term) | 
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term)
        )
    
    if department:
        courses = courses.filter(department__code=department)
        
    if level:
        # Filter by course level based on first digit in code
        courses = [c for c in courses if str(c.numeric_level) == level]
        
    if status:
        courses = courses.filter(accreditation_status=status)
    
    # Handle sorting
    sort_by = request.GET.get('sort', 'code')
    if sort_by == 'name':
        courses = courses.order_by('name')
    elif sort_by == 'updated':
        courses = courses.order_by('-updated_at')
    elif sort_by == 'status':
        courses = courses.order_by('accreditation_status')
    else:
        courses = courses.order_by('code')
    
    # Pagination
    paginator = Paginator(courses, 12)  # 12 courses per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get departments for filter dropdown
    departments = Department.objects.all()
    
    context = {
        'courses': page_obj,
        'departments': departments,
        'search_term': search_term,
        'department': department,
        'level': level,
        'status': status,
        'sort_by': sort_by
    }
    
    return render(request, 'bcit_accreditation/courses.html', context)
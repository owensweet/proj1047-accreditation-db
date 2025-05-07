from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.
def login_view(request):
    """
    Display and process the login page
    """
    return render(request, 'bcit_accreditation/bcit_accred_login.html')

def home_view(request):
    """
    Display the home page
    """
    return render(request, 'bcit_accreditation/bcit_accred_home.html')

@staff_member_required
def admin_dashboard_view(request):
    """
    Display the admin dashboard (staff only)
    """
    context = {
        'total_courses': 0,  # Replace with actual counts from your database
        'total_faculty': 0,
        'pending_updates': 0,
        'required_actions': 0,
    }
    return render(request, 'bcit_accreditation/bcit_accred_admin.html', context)

@login_required
def faculty_home_view(request):
    """
    Display the faculty home page (authenticated users only)
    """
    return render(request, 'bcit_accreditation/bcit_accred_faculty_home.html')

@login_required
def course_details_view(request, course_id=None):
    """
    Display details for a specific course
    """
    # Later you'll fetch the course from the database based on course_id
    context = {
        'course': {},  # Replace with actual course data
    }
    return render(request, 'bcit_accreditation/bcit_accred_course_details.html', context)
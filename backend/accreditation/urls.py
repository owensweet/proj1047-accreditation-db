from django.urls import path
from . import views

# Mapping the views from views.py to a url route
urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('faculty-home/', views.faculty_home_view, name='faculty_home'),
    path('course/<int:course_id>/', views.course_details_view, name='course_details'),
    path('course/', views.course_details_view, name='course_details_default'),
]
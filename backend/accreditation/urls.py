from django.urls import path
from . import views

# Mapping the views from views.py to a url route
urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('login_user/', views.login_user, name='login_user'),
    path('register/', views.register_view, name='register'),
    path('register_user/', views.register_user, name='register_user'),
    path('logout/', views.logout_user, name='logout'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('course/<int:course_id>/', views.course_details_view, name='course_details'),
    path('course/', views.course_details_view, name='course_details_default'),
    path('test/', views.test_upload_view, name='test_upload'),
    path('csv-upload/', views.csv_upload_view, name='csv_upload'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('courses/', views.courses_view, name='courses'),
]
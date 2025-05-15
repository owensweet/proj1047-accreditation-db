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
    path('csv-upload/', views.csv_upload_view, name='csv_upload'),
    
    # Multi-step form pages
    path('form/step1/', views.form_step1_view, name='form_step1'),
    path('form/step2/', views.form_step2_view, name='form_step2'),
    path('form/step3/', views.form_step3_view, name='form_step3'),
    # path('form/step4/', views.form_step4_view, name='form_step4'),
    path('form/success/', views.form_success_view, name='form_success'),
    path('form/submit/', views.form_submit_view, name='form_submit'),
    
    # Analytics page
    # path('analytics/', views.analytics_view, name='analytics'),
    path('analysis/', views.analysis_view, name='analysis'),
    
]
from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    """Department model for organizing courses"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.code}: {self.name}"

class Program(models.Model):
    """Program model for organizing courses and accreditation"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    
    def __str__(self):
        return self.name

class Course(models.Model):
    """Course model for storing course information"""
    ACCREDITATION_STATUS_CHOICES = [
        ('compliant', 'Compliant'),
        ('partial', 'Partially Compliant'),
        ('non-compliant', 'Non-Compliant'),
        ('pending', 'Pending Review'),
    ]
    
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    credits = models.DecimalField(max_digits=3, decimal_places=1)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    level = models.CharField(max_length=20, default='Undergraduate')
    accreditation_status = models.CharField(max_length=20, choices=ACCREDITATION_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code}: {self.name}"
    
    @property
    def numeric_level(self):
        """Extract numeric level from course code (e.g., COMP3800 -> 3)"""
        try:
            for char in self.code:
                if char.isdigit():
                    return int(char)
            return 0
        except:
            return 0

class LearningOutcome(models.Model):
    """Learning outcomes for courses"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='learning_outcomes')
    description = models.TextField()
    order = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.code} - Outcome {self.order}"

class GraduateAttribute(models.Model):
    """Graduate attributes that can be associated with courses"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class CourseGraduateAttribute(models.Model):
    """Many-to-many relationship between courses and graduate attributes with level"""
    LEVEL_CHOICES = [
        (1, 'Very Low (1/5)'),
        (2, 'Low (2/5)'),
        (3, 'Medium (3/5)'),
        (4, 'High (4/5)'),
        (5, 'Very High (5/5)'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='graduate_attributes')
    attribute = models.ForeignKey(GraduateAttribute, on_delete=models.CASCADE, related_name='courses')
    level = models.IntegerField(choices=LEVEL_CHOICES, default=3)
    
    def __str__(self):
        return f"{self.course.code} - {self.attribute.name}: {self.get_level_display()}"

class AssessmentMethod(models.Model):
    """Assessment methods for courses"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    name = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.course.code} - {self.name} ({self.weight}%)"

class AssessmentOutcomeMapping(models.Model):
    """Mapping between assessments and learning outcomes"""
    assessment = models.ForeignKey(AssessmentMethod, on_delete=models.CASCADE, related_name='outcomes')
    outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE, related_name='assessments')
    
    def __str__(self):
        return f"{self.assessment.name} - Outcome {self.outcome.order}"

class CSVUpload(models.Model):
    """Record of CSV file uploads"""
    DATA_TYPE_CHOICES = [
        ('course', 'Course Data'),
        ('student', 'Student Data'),
        ('program', 'Program Data'),
        ('accreditation', 'Accreditation Metrics'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('processing', 'Processing'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES)
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.file_name} - {self.file_type} ({self.status})"

class UserProfile(models.Model):
    """Extended user profile for additional user information"""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('faculty', 'Faculty Member'),
        ('staff', 'Staff Member'),
        ('viewer', 'Viewer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

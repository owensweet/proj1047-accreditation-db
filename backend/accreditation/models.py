from django.db import models
from django.core.validators import RegexValidator

class DataProcess(models.Model):
    term = models.CharField(max_length=6, primary_key=True)
    program = models.CharField(max_length=4, choices=[('ELEX', 'ELEX'), ('CIVL', 'CIVL'),
                                                      ('MECH', 'MECH'),('MINE', 'MINE')])
    course = models.CharField(max_length=8)
    gai = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.term} - {self.program} - {self.course}"

class FacultyCI(models.Model):
    course = models.CharField(max_length=8, primary_key=True)
    term = models.CharField(max_length=6)
    instructor = models.CharField(max_length=100)
    assessment_title = models.CharField(max_length=12)
    gai_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    cohort = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.course} - {self.assessment_title}"

class ProgramCI(models.Model):
    term = models.CharField(max_length=6, primary_key=True)
    ga = models.CharField(max_length=100)
    gai = models.CharField(max_length=100)
    gai_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    achievement_level = models.CharField(max_length=50)
    cohort = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.term} - {self.ga} - {self.gai}"

class AssessValidity(models.Model):
    gai = models.CharField(max_length=100, primary_key=True)
    ga = models.CharField(max_length=100)
    course = models.CharField(max_length=8)
    question_max = models.IntegerField()
    alignment = models.CharField(max_length=50, choices=[("Perfectly", "Perfectly"), ("Highly", "Highly"), ("Mostly", "Mostly"), ("Somewhat", "Somewhat")])
    gai_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    assess_max = models.IntegerField()
    assess_weight = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.course} - {self.ga}"

class AccredReport(models.Model):
    program = models.CharField(max_length=4, primary_key=True)
    term = models.CharField(max_length=6)
    ga = models.CharField(max_length=100)
    gai = models.CharField(max_length=100)
    assess_type = models.CharField(max_length=100)
    quest_text = models.CharField(max_length=400)
    alignment = models.CharField(max_length=50)
    instr_level = models.CharField(max_length=50, choices=[("Introductory", "Introductory"),
                                                           ("Intermediate", "Intermediate Development"),
                                                           ("Advanced", "Advanced Application")])
    achievement_level = models.CharField(max_length=50)
    student_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.program} - {self.term}"

class AnnualReport(models.Model):
    program = models.CharField(max_length=4, primary_key=True)
    term = models.CharField(max_length=6)
    course = models.CharField(max_length=8)
    ga = models.CharField(max_length=100)
    gai = models.CharField(max_length=100)
    student_id = models.CharField(max_length=50)
    achievement_level = models.CharField(max_length=50)
    assess_type = models.CharField(max_length=100)
    instr_comments = models.CharField(max_length=800)

    def __str__(self):
        return f"{self.program} - {self.term} - {self.course}"

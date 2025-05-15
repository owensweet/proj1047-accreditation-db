"""
This module houses the classes and methods to interact with the database.
"""
# Import models [NEEDS TO BE CHANGED/DELETED]
from .models import (
    DataProcess,
    FacultyCI,
    ProgramCI,
    AssessValidity,
    AccredReport,
    AnnualReport
)

def upload_data(program, course, term, prog_term, ):
    # Validate data here
    DataprocessDAO.insert

class DataProcessDAO:
    @staticmethod
    def insert(data):
        return DataProcess.objects.create(**data)

class FacultyCIDAO:
    @staticmethod
    def insert(data):
        return FacultyCI.objects.create(**data)

class ProgramCIDAO:
    @staticmethod
    def insert(data):
        return ProgramCI.objects.create(**data)

class AssessValidityDAO:
    @staticmethod
    def insert(data):
        return AssessValidity.objects.create(**data)
    
class AccredReportDAO:
    @staticmethod
    def insert(data):
        return AccredReport.objects.create(**data)

class AnnualReportDAO:
    @staticmethod
    def insert(data):
        return AnnualReport.objects.create(**data)

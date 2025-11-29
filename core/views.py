
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, F

# Consolidated Model Imports
from .models import (
    Student, Teacher, SchoolClass, Attendance, Fee, 
    Timetable, Result, Quiz, Course, ClassProceeding, 
    AttendanceSummary # <--- Ensure AttendanceSummary is here
)

# Consolidated Serializer Imports
from .serializers import (
    StudentSerializer, TeacherSerializer, SchoolClassSerializer, 
    AttendanceSerializer, FeeSerializer, TimetableSerializer, 
    ClassProceedingSerializer, ResultSerializer, QuizSerializer,
    AttendanceSummarySerializer # <--- Ensure AttendanceSummarySerializer is here
)

class AttendanceSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Attendance Summary data to be viewed,
    filtered by student ID.
    """
    serializer_class = AttendanceSummarySerializer
    # Only allow read-only (GET) requests
    
    # We don't use the standard queryset here because we always filter dynamically
    def get_queryset(self):
        # We need the ID of the student the Flutter app is requesting data for.
        # This relies on the URL pattern defining 'student_pk' (e.g., /api/students/1/attendance-summary/)
        student_id = self.kwargs.get('student_pk') 
        
        if student_id is not None:
            # Filter the summary data to only include records for the requested student
            # Order by percentage descending, or last_updated ascending/descending
            return AttendanceSummary.objects.filter(student__id=student_id).order_by('-percentage')
        
        # If no student ID is provided (e.g., /api/students/attendance-summary/), return an empty queryset
        return AttendanceSummary.objects.none()


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class SchoolClassViewSet(viewsets.ModelViewSet):
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer

class FeeViewSet(viewsets.ModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer

class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class ClassProceedingsView(APIView):
    # This line has been commented out to temporarily disable authentication.
    # When your login system is complete, you should uncomment it.
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # This is a temporary fix to bypass the user authentication check.
        # We will get the first student in the database and use them.
        student = Student.objects.first()
        if not student:
            return Response({'error': 'No students found in the database.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get all attendance records for the student
        attendance_records = Attendance.objects.filter(student=student)

        # Group attendance records by course to get class proceeding info
        courses = attendance_records.values('course').annotate(
            subject=F('course__subject'), # <-- Corrected to use 'subject' field
            teacher_first_name=F('course__teacher__first_name'),
            teacher_last_name=F('course__teacher__last_name'),
            total_classes=Count('id'),
            attended=Count('id', filter=Q(status='Present')),
            absent=Count('id', filter=Q(status='Absent'))
        ).order_by('subject')

        data = []
        for c in courses:
            data.append({
                'subject': c['subject'],
                'teacher': f"{c['teacher_first_name']} {c['teacher_last_name']}",
                'total_classes': c['total_classes'],
                'attended': c['attended'],
                'absent': c['absent'],
                'section': 'A',
            })
        
        # Directly return the list of dicts
        return Response(data)
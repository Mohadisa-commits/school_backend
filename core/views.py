from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated # REQUIRED FOR SECURE FILTERING
from django.db.models import Count, Q, F

# Consolidated Model Imports
from .models import (
    Student, Teacher, SchoolClass, Attendance, Fee, 
    Timetable, Result, Quiz, Course, ClassProceeding, 
    AttendanceSummary 
)

# Consolidated Serializer Imports
from .serializers import (
    StudentSerializer, TeacherSerializer, SchoolClassSerializer, 
    AttendanceSerializer, FeeSerializer, TimetableSerializer, 
    ClassProceedingSerializer, ResultSerializer, QuizSerializer,
    AttendanceSummarySerializer 
)

# --- HELPER FUNCTION: Find the Student related to the logged-in User ---
def get_student_for_user(user):
    """Retrieves the Student object linked to the currently logged-in Django User."""
    try:
        # Assumes the Student model has a ForeignKey or OneToOneField called 'user'
        return Student.objects.get(user=user)
    except Student.DoesNotExist:
        return None

# --- CORE VIEWSETS (Student-Specific Filtering) ---

class StudentViewSet(viewsets.ModelViewSet):
    """API endpoint to get the single Student record for the logged-in user."""
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return the student record linked to the logged-in Django user
        if self.request.user.is_authenticated:
            return Student.objects.filter(user=self.request.user)
        return Student.objects.none()

class FeeViewSet(viewsets.ModelViewSet):
    """API endpoint to get Fee records specific to the logged-in student."""
    serializer_class = FeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student = get_student_for_user(self.request.user)
        if student:
            # Filter Fee records by the retrieved student
            return Fee.objects.filter(student=student)
        return Fee.objects.none()

class ResultViewSet(viewsets.ModelViewSet):
    """API endpoint to get Result records specific to the logged-in student."""
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student = get_student_for_user(self.request.user)
        if student:
            # Filter Result records by the retrieved student
            return Result.objects.filter(student=student)
        return Result.objects.none()

class QuizViewSet(viewsets.ModelViewSet):
    """API endpoint to get Quiz records specific to the logged-in student."""
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student = get_student_for_user(self.request.user)
        if student:
            # Filter Quiz records by the retrieved student
            return Quiz.objects.filter(student=student)
        return Quiz.objects.none()

class AttendanceViewSet(viewsets.ModelViewSet):
    """API endpoint to get individual Attendance records specific to the logged-in student."""
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        student = get_student_for_user(self.request.user)
        if student:
            # Filter Attendance records by the retrieved student
            return Attendance.objects.filter(student=student)
        return Attendance.objects.none()

class ClassProceedingsView(APIView):
    """Calculates and returns class proceedings (attendance summary) for the logged-in student."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = get_student_for_user(request.user)
        
        # Ensure the user is a valid, linked student
        if not student:
            return Response({'error': 'User is not linked to a student record.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get all attendance records for the specific, logged-in student
        attendance_records = Attendance.objects.filter(student=student)
        
        # --- (Rest of the calculation logic remains the same) ---
        
        # Group attendance records by course to get class proceeding info
        courses = attendance_records.values('course').annotate(
            subject=F('course__subject'), 
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
                'section': student.school_class.name if student.school_class else 'N/A', # Use the student's actual class
            })
        
        return Response(data)

# --- GENERIC VIEWSETS (No Filtering Required) ---

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    # Teachers can be viewed by anyone, but we should restrict modifications
    permission_classes = [IsAuthenticated] # Ensures only logged-in users can view

class SchoolClassViewSet(viewsets.ModelViewSet):
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer
    permission_classes = [IsAuthenticated]

class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]

class AttendanceSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    # This view is a special case: it relies on the URL to filter (e.g., /students/{id}/...)
    # No changes are needed here, as the URL structure already determines the data.
    serializer_class = AttendanceSummarySerializer
    
    def get_queryset(self):
        student_id = self.kwargs.get('student_pk') 
        if student_id is not None:
            return AttendanceSummary.objects.filter(student__id=student_id).order_by('-percentage')
        return AttendanceSummary.objects.none()
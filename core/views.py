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
    AttendanceSummary 
)

# Consolidated Serializer Imports
from .serializers import (
    StudentSerializer, TeacherSerializer, SchoolClassSerializer, 
    AttendanceSerializer, FeeSerializer, TimetableSerializer, 
    ClassProceedingSerializer, ResultSerializer, QuizSerializer,
    AttendanceSummarySerializer 
)

# --- CORE VIEWSETS (Student-Specific Filtering) ---
# These views now only return data belonging to the logged-in user.

class StudentViewSet(viewsets.ModelViewSet):
    """API endpoint to get the single Student record for the logged-in user."""
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 1. Check if the user is logged in
        if not self.request.user.is_authenticated:
            return Student.objects.none()
            
        # 2. Filter the Student model based on the logged-in user
        # Direct filter: Student.user matches the logged-in user object
        return Student.objects.filter(user=self.request.user)

class FeeViewSet(viewsets.ModelViewSet):
    """API endpoint to get Fee records specific to the logged-in student."""
    serializer_class = FeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Fee.objects.none()
            
        # Direct filter by traversing Foreign Key: Fee -> Student -> User
        return Fee.objects.filter(student__user=self.request.user)

class ResultViewSet(viewsets.ModelViewSet):
    """API endpoint to get Result records specific to the logged-in student."""
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Result.objects.none()
            
        # Direct filter by traversing Foreign Key: Result -> Student -> User
        return Result.objects.filter(student__user=self.request.user)

class QuizViewSet(viewsets.ModelViewSet):
    """API endpoint to get Quiz records specific to the logged-in student."""
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Quiz.objects.none()
            
        # Direct filter by traversing Foreign Key: Quiz -> Student -> User
        return Quiz.objects.filter(student__user=self.request.user)

class AttendanceViewSet(viewsets.ModelViewSet):
    """API endpoint to get individual Attendance records specific to the logged-in student."""
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Attendance.objects.none()
            
        # Direct filter by traversing Foreign Key: Attendance -> Student -> User
        return Attendance.objects.filter(student__user=self.request.user)

class ClassProceedingsView(APIView):
    """Calculates and returns class proceedings (attendance summary) for the logged-in student."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
             return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
             
        # Find the specific student linked to the logged-in user using direct lookup
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
             return Response({'error': 'Logged-in user is not linked to a student record.'}, status=status.HTTP_404_NOT_FOUND)

        # The rest of the logic uses the found 'student' object
        attendance_records = Attendance.objects.filter(student=student)
        
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
                'section': student.school_class.name if student.school_class else 'N/A',
            })
        
        return Response(data)

# --- GENERIC VIEWSETS (No Filtering Required) ---

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

class SchoolClassViewSet(viewsets.ModelViewSet):
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer
    permission_classes = [IsAuthenticated]

class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]

class AttendanceSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttendanceSummarySerializer
    
    def get_queryset(self):
        student_id = self.kwargs.get('student_pk') 
        if student_id is not None:
            return AttendanceSummary.objects.filter(student__id=student_id).order_by('-percentage')
        return AttendanceSummary.objects.none()
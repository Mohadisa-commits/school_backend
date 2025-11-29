from rest_framework import serializers

# Import ALL models that are used in the serializers below
from .models import (
    Student, Teacher, SchoolClass, Attendance, Fee, Timetable,
    Result, Quiz, Course, AttendanceSummary # <--- ADDED Course and AttendanceSummary
)

# ------------------- Student, Teacher, Class -------------------
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class SchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = '__all__'

# ------------------- Attendance & Fee -------------------
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = '__all__'

# ------------------- Timetable -------------------
from rest_framework import serializers
# Make sure to import your Timetable model from wherever it is defined
# from .models import Timetable 

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = (
            'id', 
            'day', 
            'subject', 
            'start_time', 
            'end_time',
            'teacher', # The teacher ID
            
            # ✅ ALL NEW FIELDS MUST BE INCLUDED HERE ✅
            'room',    
            'location', 
            'section', 
            'courseCode', # Added from the model
            'status',     # Added from the model
        )

# ------------------- Results & Quizzes -------------------
class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

# ------------------- ClassProceeding (computed, not model) -------------------
class ClassProceedingSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=100)
    teacher = serializers.CharField(max_length=100)
    section = serializers.CharField(max_length=50)
    total_classes = serializers.IntegerField()
    attended = serializers.IntegerField()
    absent = serializers.IntegerField()

# ------------------- Automated Attendance Summary -------------------
class AttendanceSummarySerializer(serializers.ModelSerializer):
    # CRITICAL FIX: The source field must match the model relationship (course)
    # The output field name should be clear, like 'subject_name'
    subject_name = serializers.CharField(source='course.name', read_only=True)
    
    # We no longer need student_id in the output since the ViewSet already filters by it.
    
    class Meta:
        model = AttendanceSummary
        # Use the corrected field name
        fields = ['id', 'subject_name', 'percentage', 'last_updated']
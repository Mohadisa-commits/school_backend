from rest_framework import serializers

# Import ALL models that are used in the serializers below
from .models import (
    Student, Teacher, SchoolClass, Attendance, Fee, Timetable,
    Result, Quiz, Course, AttendanceSummary # <--- ADDED Course and AttendanceSummary
)

# ------------------- Student, Teacher, Class -------------------
class StudentSerializer(serializers.ModelSerializer):
    # CRITICAL FIX: Include the SchoolClass name for easy display in Flutter
    school_class_name = serializers.CharField(source='school_class.name', read_only=True)
    
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
class TimetableSerializer(serializers.ModelSerializer):
    # CRITICAL FIX: Return the teacher's full name instead of just the ID.
    teacher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Timetable
        # Use '__all__' to ensure every new field is included automatically.
        fields = '__all__' 
        
    def get_teacher_name(self, obj):
        if obj.teacher:
            return f"{obj.teacher.first_name} {obj.teacher.last_name}"
        return "TBD"

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
    
    class Meta:
        model = AttendanceSummary
        # Use the corrected field name
        fields = ['id', 'subject_name', 'percentage', 'last_updated']
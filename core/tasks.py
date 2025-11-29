# C:\Users\Fast\Desktop\school_backend\core\tasks.py

from background_task import background
from django.utils import timezone
from django.db.models import Q
# FIX 1: Import the CORRECT models you defined in models.py
# (Student, Course, Attendance, AttendanceSummary)
from .models import Student, Course, Attendance, AttendanceSummary 

# Schedule to run every 12 hours (43200 seconds). 
@background(schedule=43200, name='calculate_all_attendance_summary') 
def calculate_all_attendance():
    """
    Calculates the aggregate attendance percentage for all students 
    and updates the AttendanceSummary table.
    """
    print(f"--- Starting Attendance Calculation at {timezone.now()} ---")
    
    # Check if the models exist and have data
    # FIX 2: Check Student and Course existence (using the correct model names)
    if not Student.objects.exists() or not Course.objects.exists():
        print("Required Student or Course data is missing. Task aborted.")
        return

    # Iterate through all students and all courses
    for student in Student.objects.all():
        for course in Course.objects.all():
            
            # 1. Total Classes Held (Denominator)
            # Count all attendance records for this student and course
            total_classes = Attendance.objects.filter(
                student=student, 
                course=course
            ).count()
            
            # 2. Classes Attended (Numerator)
            # Count only the 'Present' records for this student and course
            classes_attended = Attendance.objects.filter(
                student=student, 
                course=course,
                status='Present' # This status value is correct
            ).count()
            
            
            # 3. Calculate percentage
            if total_classes > 0:
                percentage = (classes_attended / total_classes) * 100
            else:
                percentage = 0.0
                
            # 4. Update or create the summary record
            # FIX 3: Use 'course' instead of 'subject' in update_or_create
            summary, created = AttendanceSummary.objects.update_or_create(
                student=student, 
                course=course,
                defaults={'percentage': percentage}
            )
            print(f"[{'CREATED' if created else 'UPDATED'}] {student.first_name} - {course.name}: {percentage:.2f}%")

    print("--- Attendance Calculation Finished ---")

# Schedule the task to run for the first time 
# We'll set the repeat to 10 seconds for initial testing, then switch to 43200.
# Set the initial run time to 60 seconds after startup.
calculate_all_attendance(schedule=60, repeat=43200, repeat_until=None)
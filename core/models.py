from django.db import models
from django.contrib.auth.models import User

class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
        
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    grade = models.CharField(max_length=10)
    attendance = models.IntegerField(default=0)
    # CRITICAL: Assuming you have a Foreign Key here, we need to ensure it's defined!
    # If the student model is not linked to a class, the timetable will never filter.
    # I am adding it here as it is highly likely missing or needed for the filter chain.
    school_class = models.ForeignKey('SchoolClass', on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Course(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    subject = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class SchoolClass(models.Model):
    name = models.CharField(max_length=50)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[("Present", "Present"), ("Absent", "Absent")], default="Present")

class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)

# In core/models.py
class Timetable(models.Model):
    # 1. DEFINE THE CHOICES
    DAY_CHOICES = [
        ('Mon', 'Monday'), 
        ('Tue', 'Tuesday'), 
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'), 
        ('Fri', 'Friday'), 
        ('Sat', 'Saturday'), 
        ('Sun', 'Sunday'),
    ]
    
    # CRITICAL FIX: The link to SchoolClass must exist for filtering!
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="timetable_entries")
    
    # 2. FIELD DECLARATIONS
    day = models.CharField(max_length=3, choices=DAY_CHOICES) 
    subject = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    # ✅ CORRECTED NEW FIELDS ✅
    room = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    section = models.CharField(max_length=50, blank=True, null=True)
    courseCode = models.CharField(max_length=15, blank=True, null=True) 
    status = models.CharField(max_length=10, blank=True, null=True) 
    
    class Meta:
        # Note: If you add 'school_class' here, you must run migrations.
        unique_together = ('day', 'start_time', 'school_class') 
        ordering = ['day', 'start_time']

    def __str__(self):
        teacher_name = f"{self.teacher.first_name} {self.teacher.last_name}" if self.teacher else "No teacher"
        return f"{self.day} - {self.subject} ({teacher_name}) {self.start_time}-{self.end_time}"
        
class ClassProceeding(models.Model):
    subject = models.CharField(max_length=100)
    teacher = models.CharField(max_length=100)
    section = models.CharField(max_length=50)
    total_classes = models.IntegerField()
    attended = models.IntegerField()
    absent = models.IntegerField()

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    score = models.IntegerField()
    grade = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.student}'s result for {self.subject}"

class Quiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    date = models.DateField()
    score = models.IntegerField()

    def __str__(self):
        return f"{self.student}'s quiz in {self.subject}"

# In core/models.py, ADD THIS NEW MODEL

class AttendanceSummary(models.Model):
    # Links to the student and the course
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE) 
    
    # The final, calculated percentage
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0) 
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensures a student only has one summary per course
        unique_together = ('student', 'course') 

    def __str__(self):
        return f"{self.student.first_name} - {self.course.name}: {self.percentage}%"
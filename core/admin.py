from django.contrib import admin
from .models import AttendanceSummary 
from .models import (
    Student, Teacher, SchoolClass, Attendance, Fee,
    Timetable, Result, Quiz, Course, ClassProceeding
)


admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(SchoolClass)
admin.site.register(Attendance)
admin.site.register(Fee)
admin.site.register(Timetable)
admin.site.register(Result)
admin.site.register(Quiz)
admin.site.register(Course)
admin.site.register(ClassProceeding)
admin.site.register(AttendanceSummary) 


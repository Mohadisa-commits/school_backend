"""
URL configuration for school_api project.
"""
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as auth_views # <--- ADD THIS LINE
from rest_framework import routers
from core.views import (
    StudentViewSet, 
    TeacherViewSet, 
    SchoolClassViewSet, 
    AttendanceViewSet, 
    FeeViewSet, 
    TimetableViewSet,
    ClassProceedingsView,
    ResultViewSet, 
    QuizViewSet,
    AttendanceSummaryViewSet, # <--- Correctly imported
)

router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'classes', SchoolClassViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'fees', FeeViewSet)
router.register(r'timetable', TimetableViewSet) 
router.register(r'results', ResultViewSet) 
router.register(r'quizzes', QuizViewSet) 

# REGISTER THE CUSTOM, NESTED ROUTE FOR ATTENDANCE SUMMARY
# This creates the URL: /api/students/{student_id}/attendance-summary/
router.register(r'students/(?P<student_pk>\d+)/attendance-summary', 
                AttendanceSummaryViewSet, 
                basename='attendance-summary')

def home(request):
    return HttpResponse("<h1>Welcome to School API</h1><p>Use /api/ to access endpoints.</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', home),
    path('api/api-token-auth/', auth_views.obtain_auth_token),

    # The ClassProceedingsView (an APIView) must be registered separately
    path('api/class_proceedings/', ClassProceedingsView.as_view(), name='class_proceedings'), 
]
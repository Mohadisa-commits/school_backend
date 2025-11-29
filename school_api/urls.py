# Assuming your imports at the top look like this (do not change the imports):
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from core.views import (
    StudentViewSet, TeacherViewSet, SchoolClassViewSet, AttendanceViewSet,
    FeeViewSet, TimetableViewSet, ResultViewSet, QuizViewSet,
    AttendanceSummaryViewSet, ClassProceedingsView
)
from rest_framework.authtoken import views as authtoken_views

router = routers.DefaultRouter()

# --- CORRECTED REGISTRATIONS (Added 'basename' to all custom viewsets) ---

# These custom viewsets use get_queryset and need a defined basename.
router.register(r'students', StudentViewSet, basename='student')
router.register(r'fees', FeeViewSet, basename='fee')
router.register(r'results', ResultViewSet, basename='result')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'attendances', AttendanceViewSet, basename='attendance')

# These generic viewsets have a static 'queryset' and do not strictly need 'basename'.
router.register(r'teachers', TeacherViewSet)
router.register(r'classes', SchoolClassViewSet)
router.register(r'timetables', TimetableViewSet)

# Registering nested Attendance Summary (READ-ONLY)
# The parent lookup for the student is done automatically by the simple router.
# The `basename` is necessary here too.
router.register(r'students/(?P<student_pk>[^/.]+)/attendancesummary', 
                AttendanceSummaryViewSet, basename='attendance-summary')

# ------------------------------------------------------------------------

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', authtoken_views.obtain_auth_token),
    path('api/proceedings/', ClassProceedingsView.as_view()),
]
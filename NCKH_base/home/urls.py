from django.urls import path
from . import views
urlpatterns = [
    path('home/', views.home, name='home'),
    path('coming-soon/<str:feature_name>/', views.placeholder_view, name='placeholder_feature'),
    path('profile/', views.student_profile_view, name='student_profile'),
    path('student_curriculum_sparql_view/', views.student_curriculum_sparql_view, name='student_curriculum_sparql_view'),
    path('grades/', views.student_grades_view, name='student_grades'),
    path('curriculum/', views.curriculum, name='curriculum'),
]
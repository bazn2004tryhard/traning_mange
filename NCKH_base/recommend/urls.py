from django.urls import path
from . import views
urlpatterns = [
    path('course_graph_view/', views.course_graph_view, name = 'course_graph_view'),
    path('curriculumGraph/', views.curriculumGraph, name = 'curriculumGraph'),
]
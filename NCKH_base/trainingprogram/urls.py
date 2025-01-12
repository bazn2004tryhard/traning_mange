
from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.training_program_list, name='training_program_list'),
    path('program/<str:program_id>/list_course_by_program', views.course_by_program, name='course_by_program'),
    path('program/add/', views.training_program_form, name='training_program_add'),
    path('program/<str:program_id>/edit/', views.training_program_form, name='training_program_edit'),
    path('program/<str:program_id>/delete/', views.training_program_delete, name='training_program_delete'),
]
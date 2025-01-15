
from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.training_program_list, name='training_program_list'),
    # thêm sửa xóa các bảng 
    # bảng trainingprogram
    path('program/<str:program_id>/list_course_by_program', views.course_by_program, name='course_by_program'),
    path('program/add/', views.training_program_form, name='training_program_add'),
    path('program/<str:program_id>/edit/', views.training_program_form, name='training_program_edit'),
    path('program/<str:program_id>/delete/', views.training_program_delete, name='training_program_delete'),
    # dùng để imort file csv 
    path('import_training_program/', views.import_training_program, name='import_training_program'),  # Upload và xem trước
    path('confirm_import_training_program/', views.confirm_import_training_program, name='confirm_import_training_program'),  # Xác nhận

    #  bảng course
    path('course/list_of_courses',views.list_of_courses,name='list_of_courses'),
    path('course/add',views.course_form, name='course_add'),
    path('course/<str:course_id>/edit',views.course_form, name='course_edit'),
    path('course/<str:course_id>/delete',views.course_delete, name='course_delete'),
    # dùng để imort file csv 
    path('import_courses/', views.import_courses, name='import_courses'),  # Upload và xem trước
    path('confirm_courses/', views.confirm_courses, name='confirm_courses'),  # Xác nhận

    # bảng course_training_program
    path('course_training_program/list_of_course_training_program',views.list_of_course_training_program,name='list_of_course_training_program'),
    # dùng để imort file csv 
    path('course_training_program/import_courses_program', views.import_courses_program, name='import_courses_program'),  # Upload và xem trước
     path('course_training_program/confirm_courses_program', views.confirm_courses_program, name='confirm_courses_program'),  # Xác nhận

]
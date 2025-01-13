
from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.training_program_list, name='training_program_list'),
    # thêm sửa xóa các bảng 
    path('program/<str:program_id>/list_course_by_program', views.course_by_program, name='course_by_program'),
    path('program/add/', views.training_program_form, name='training_program_add'),
    path('program/<str:program_id>/edit/', views.training_program_form, name='training_program_edit'),
    path('program/<str:program_id>/delete/', views.training_program_delete, name='training_program_delete'),
    # dùng để imort file csv
    path('import_training_program/', views.import_training_program, name='import_training_program'),  # Upload và xem trước
    path('confirm_import_training_program/', views.confirm_import_training_program, name='confirm_import_training_program'),  # Xác nhận
]
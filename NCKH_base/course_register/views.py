from django.shortcuts import render, redirect
from trainingprogram.models import User, Course, Student, Grade

# Create your views here.

# Hàm lấy địa chỉ trang đăng kí
def f1(request):
    return render(request, "course_register/site_course_register.html")

# Hàm đăng kí môn
def f2(request, course_id):
    student = request.user.student
    course = Course.objects.get(course_id=course_id)
    sum_credits = 0 # Khởi tạo tổng tín chỉ
    # student = Student.objects.get(user=request.user) # Lấy danh nghĩa học sinh của người dùng hiện tại
    enrolled = Grade.objects.filter(student=student) # Lấy danh sách các bản ghi đã đăng kí môn của học sinh hiện tại
    for object in enrolled: # Duyệt danh sách bản ghi đó để tính tổng tín chỉ
        sum_credits += object.course.credits
    if Grade.objects.filter(student=student, course=course).exists():# Kiểm tra xem tồn tại bản ghi đó chưa, nếu rồi thì gửi phản hồi lỗi, thoát hàm
        return redirect('f1')
    # Kiểm tra xem đạt giới hạn tín chỉ chưa, nếu rồi thì gửi phản hồi lỗi, thoát hàm
    if sum_credits >= 33: # Thiếu dấu '=', vì load trước mới đăng kí nên gặp lỗi vẫn cho đăng kí thêm 1 môn nữa
        return redirect('f1')
    Grade.objects.create(student=student, course=course)# Không bị gì thì thêm bản ghi mới
    return redirect('f1')
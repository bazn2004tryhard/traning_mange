from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from trainingprogram.models import User, Course, Student, Grade, TrainingProgram, CourseTrainingProgram
from django.db.models import Q

# Create your views here.

# Hàm lấy địa chỉ trang đăng kí
def f1(request):
    context = {
        'danhsachkhoahoc': Course.objects.all()     
    }
    return render(request, "course_register/site_course_register.html", context)

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


#Hàm hiển thị các môn gợi ý đăng kí
@login_required
def f3(request):
    stu = request.user.student
    pro = TrainingProgram.objects.get(major = stu.major, StartYear = stu.AcademicYear)
    # mon_in_ct_daotao = CourseTrainingProgram.objects.filter(program = pro.program_id)
    mon_in_ct_daotao = Course.objects.filter(course_for__program = pro)

    ds_id_mon_da_dang_ki = Grade.objects.filter(
        student=stu  # Chỉ lấy điểm của sinh viên hiện tại
    ).values_list(
        'course__course_id',  # Lấy primary key của các Course liên quan
        flat=True  # Trả về danh sách phẳng [pk1, pk2, ...]
    )

    # Query Course
    ds_mon_chua_hoc = mon_in_ct_daotao.exclude(
        pk__in=list(ds_id_mon_da_dang_ki)  # Loại trừ những Course có pk nằm trong danh sách đã có điểm
    )

    #Cac mon khong co tien quyet
    q1 = Q(prerequisites__isnull = True)
    ds_mon_tien_quyet_cua_chua_hoc = ds_mon_chua_hoc.filter(q1).distinct()

    #Cac mon diem thap
    que1 = Grade.objects.filter(Result__lte = 4)

    #Cac mon du dieu kien hoc

    context = {
        'ct_daotao' : pro,
        'mon_in_ct_daotao' : mon_in_ct_daotao,
        'ds_id_mon_da_dang_ki' : ds_id_mon_da_dang_ki,
        'ds_mon_chua_hoc' : ds_mon_chua_hoc,
        'ds_mon_tien_quyet_cua_chua_hoc' : ds_mon_tien_quyet_cua_chua_hoc,
        'que1' : que1,
    }
    return render(request,"course_register/goiy.html", context)
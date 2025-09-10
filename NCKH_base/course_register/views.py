from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from trainingprogram.models import User, Course, Student, Grade, TrainingProgram, CourseTrainingProgram, OptionalGroup
from django.db.models import Q, OuterRef, Exists, Sum

# Create your views here.

# Hàm lấy địa chỉ trang đăng kí
def f1(request):
    student = request.user.student  # Lấy đối tượng Student từ User đang đăng nhập

    # 1. Lấy ngành của sinh viên
    student_major = student.major

    # 2. Lấy năm nhập học của sinh viên (từ model Student)
    # Giả sử trường AcademicYear lưu năm dưới dạng chuỗi hoặc số nguyên
    student_enrollment_year = int(student.AcademicYear)  # Chuyển sang int nếu cần so sánh

    # 3. Tìm chương trình đào tạo phù hợp
    # Lọc các TrainingProgram thuộc về ngành của sinh viên VÀ có StartYear khớp với năm nhập học
    try:
        training_program = TrainingProgram.objects.get(
            major=student_major,
            StartYear=student_enrollment_year
        )
    except TrainingProgram.DoesNotExist:
        training_program = None
    except TrainingProgram.MultipleObjectsReturned:
        # Xử lý trường hợp có nhiều chương trình đào tạo khớp (hiếm khi xảy ra nếu dữ liệu chuẩn)
        # Có thể lấy cái đầu tiên hoặc báo lỗi tùy theo logic bạn muốn
        training_program = TrainingProgram.objects.filter(
            major=student_major,
            StartYear=student_enrollment_year
        ).first()
        # Hoặc:
        # context = {'error_message': "Tìm thấy nhiều chương trình đào tạo phù hợp."}
        # return render(request, 'trainingprogram/training_program.html', context)

    # 4. Lấy danh sách các môn học (CourseTrainingProgram) của chương trình đào tạo đó
    courses_in_program = []
    program_total_credits = 0
    if training_program:
        # Sử dụng related_name 'program_for' từ TrainingProgram đến CourseTrainingProgram
        # hoặc query trực tiếp CourseTrainingProgram
        course_training_program_links = CourseTrainingProgram.objects.filter(
            program=training_program
        ).order_by('semester', 'course__course_name')  # Sắp xếp theo học kỳ, rồi theo tên môn học

        for link in course_training_program_links:
            courses_in_program.append({
                'course_id': link.course.course_id,
                'course_name': link.course.course_name,
                'credits': link.course.credits,
                'semester': link.semester,
                'course_type': link.get_course_type_display(),  # Hiển thị giá trị dễ đọc của course_type
                'prerequisites': ", ".join(
                    [prereq.course_name for prereq in link.course.prerequisites.all()]) or "Không có",
                'optional_group': link.option_G.group_name if link.option_G else None
            })
            program_total_credits += link.course.credits

    context = {
        # 'student': student,
        # 'training_program': training_program,
        'danhsachkhoahoc': courses_in_program,
        # 'program_total_credits': program_total_credits,
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
    student = request.user.student
    student_major = student.major
    # 2. Lấy năm nhập học của sinh viên (từ model Student)
    # Giả sử trường AcademicYear lưu năm dưới dạng chuỗi hoặc số nguyên
    student_enrollment_year = int(student.AcademicYear)  # Chuyển sang int nếu cần so sánh
    # 3. Tìm chương trình đào tạo phù hợp
    # Lọc các TrainingProgram thuộc về ngành của sinh viên VÀ có StartYear khớp với năm nhập học
    try:
        training_program = TrainingProgram.objects.get(
            major=student_major,
            StartYear=student_enrollment_year
        )
    except TrainingProgram.DoesNotExist:
        training_program = None
    except TrainingProgram.MultipleObjectsReturned:
        # Xử lý trường hợp có nhiều chương trình đào tạo khớp (hiếm khi xảy ra nếu dữ liệu chuẩn)
        # Có thể lấy cái đầu tiên hoặc báo lỗi tùy theo logic bạn muốn
        training_program = TrainingProgram.objects.filter(
            major=student_major,
            StartYear=student_enrollment_year
        ).first()

    # mon_in_ct_daotao = CourseTrainingProgram.objects.filter(program = training_program.program_id)
    #Cac mon trog ctdt cua sinh vien hien tai
    mon_in_ct_daotao = Course.objects.filter(course_for__program = training_program)
    #Cac mon da dang ki
    ds_id_mon_da_dang_ki = Grade.objects.filter(
        student=student
    ).values_list(
        'course__course_id',  # Lấy primary key của các Course liên quan
        flat=True  # Trả về danh sách phẳng [pk1, pk2, ...]
    )

    # Query Course chua hoc
    ds_mon_chua_hoc = mon_in_ct_daotao.exclude(
        pk__in=list(ds_id_mon_da_dang_ki)  # Loại trừ những Course có pk nằm trong danh sách đã có điểm
    )

    bat_buoc_chua_hoc = ds_mon_chua_hoc.filter(course_for__course_type=0)

    #Cac mon khong co tien quyet
    q1 = Q(prerequisites__isnull = True)
    ds_mon_tien_quyet_cua_chua_hoc = ds_mon_chua_hoc.filter(q1).distinct()

    #Cac mon diem thap
    que1 = Grade.objects.filter(FinalExamScore__lt = 4)

    #Cac mon đã đạt
    que2 = Grade.objects.filter(student = student.pk, Result__gte = 4)

    #ds ID các mon da dat
    que3 = que2.values_list('course__pk', flat = True)

    #sub querry ds mon ko du dieu kien
    con1 = Q(prerequisite_for = OuterRef('pk'))
    con2 = ~Q(pk__in = que3)
    que4 = Course.objects.filter(con1 & con2)

    #ds Cac mon du dieu kien
    que5 = ds_mon_chua_hoc.exclude(Exists(que4))

    #goi y cac mon trong nhom tu chon ma hoc chua du tin chi
    #1 tinh so tin chi da hoc trong cung nhom
    #1.1 lay cac nhom
    que6 = OptionalGroup.objects.all()
    l = set() #Danh sach lay id nhom hoc thieu
    for ban_ghi in que6:
        count_tin_da_hoc = CourseTrainingProgram.objects.filter(course__pk__in = ds_id_mon_da_dang_ki , program = training_program, option_G = ban_ghi.pk).aggregate(Sum('course__credits')) # Tra ve dict
        # l.append(count_tin_da_hoc)
        if count_tin_da_hoc.get('course__credits__sum') is None or count_tin_da_hoc.get('course__credits__sum') < ban_ghi.min_credits:
            l.add(ban_ghi.pk)
    l = list(l)
    #2 lay cac mon trong cac nhom hoc thieu, loại tru các môn đã đăng kí
    que7 = Course.objects.filter(course_for__option_G__in = l).exclude(pk__in = ds_id_mon_da_dang_ki) #Cac mon trong nhom hoc thieu

    context = {
        'ct_daotao' : training_program,
        'mon_in_ct_daotao' : mon_in_ct_daotao,
        'ds_id_mon_da_dang_ki' : ds_id_mon_da_dang_ki,
        'ds_mon_chua_hoc' : ds_mon_chua_hoc,
        'ds_mon_tien_quyet_cua_chua_hoc' : ds_mon_tien_quyet_cua_chua_hoc,
        'que1' : que1,
        'que2' : que2,
        'que3': que3,
        'que5' : que5,
        'que6' : que6,
        'l' : l,
        'que7' : que7,
        'bat_buoc_chua_hoc' : bat_buoc_chua_hoc,
    }
    return render(request,"course_register/goiy.html", context)

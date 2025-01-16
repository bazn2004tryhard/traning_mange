from django.shortcuts import render
from django.contrib import messages
import csv
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import TrainingProgram, Course, CourseTrainingProgram
from .forms import TrainingProgramForm, CourseForm, CourseTrainingProgramForm
def training_program_list(request):
    training_programs = TrainingProgram.objects.all()
    return render(request, 'trainingprogram/training_program_list.html', {'training_programs': training_programs})

# Thêm/Sửa TrainingProgram
def training_program_form(request, program_id=None):
    if program_id:
        program = get_object_or_404(TrainingProgram, program_id=program_id)
    else:
        program = None
    
    form = TrainingProgramForm(request.POST or None, instance=program)
    if form.is_valid():
        form.save()
        return redirect('training_program_list')
    
    return render(request, 'trainingprogram/training_program_form.html', {'form': form})

# Xóa TrainingProgram
def training_program_delete(request, program_id):
    program = get_object_or_404(TrainingProgram, program_id=program_id)
    if request.method == 'POST':
        program.delete()
        return redirect('training_program_list')
    
    context = {
        'title': 'Xóa Chương trình đào tạo',
        'program': program,
    }
    return render(request, 'trainingprogram/training_program_delete.html', context)
# Danh sách Course theo TrainingProgram
def course_by_program(request, program_id):
    program = get_object_or_404(TrainingProgram, program_id=program_id)
    courses = CourseTrainingProgram.objects.filter(program=program).select_related('course')
    return render(request, 'trainingprogram/course_by_program.html', {'program': program, 'courses': courses})

# xử lý upload và xem trước 
import csv
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import TrainingProgram, Major

# Xử lý import dữ liệu từ CSV
def import_training_program(request):
    if request.method == 'POST' and 'file' in request.FILES:
        csv_file = request.FILES['file']

        # Kiểm tra định dạng file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File không đúng định dạng CSV.')
            return redirect('training_program_list')

        try:
            # Đọc dữ liệu từ file CSV
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            # Chuẩn bị dữ liệu xem trước
            data_preview = []
            for row in reader:
                program_id = row.get('program_id')
                program_name = row.get('program_name')
                start_year = row.get('StartYear')
                major_id = row.get('major')  # Lấy id của Major từ CSV

                # Lấy Major từ database theo tên (có thể thay đổi theo cách bạn muốn xử lý)
                try:
                    major = Major.objects.get(major_id=major_id)
                except Major.DoesNotExist:
                    major = None  # Nếu không tìm thấy Major, có thể tạo mới hoặc thông báo lỗi

                data_preview.append({
                    'program_id': program_id,
                    'program_name': program_name,
                    'StartYear': start_year,
                    'major': major,  # Hiển thị Major nếu có
                })

            # Reset lại con trỏ file để có thể đọc lại lần nữa trong hàm xác nhận import
            csv_file.seek(0)

            return render(request, 'trainingprogram/import_preview.html', {'data_preview': data_preview, 'csv_file': csv_file})

        except Exception as e:
            messages.error(request, f'Đã xảy ra lỗi khi đọc file: {e}')
            return redirect('training_program_list')

    return redirect('training_program_list')


# xử lý lưu vào cơ sở dữ liệu
# Xử lý xác nhận và lưu dữ liệu vào cơ sở dữ liệu
def confirm_import_training_program(request):
    if request.method == 'POST':
        program_ids = request.POST.getlist('program_id')
        program_names = request.POST.getlist('program_name')
        start_years = request.POST.getlist('StartYear')
        major_ids = request.POST.getlist('major')  # Danh sách id major

        # Lưu dữ liệu vào cơ sở dữ liệu
        try:
            for program_id, program_name, start_year, major_id in zip(program_ids, program_names, start_years, major_ids):
                # Kiểm tra nếu Major có tồn tại
                try:
                    major = Major.objects.get(major_id=major_id)
                except Major.DoesNotExist:
                    major = None  # Nếu không tìm thấy, có thể xử lý tùy ý, ví dụ tạo mới

                # Nếu không có, báo lỗi hoặc tạo mới Major ở đây
                if not major:
                    messages.error(request, f'Major "{major_id}" không tồn tại.')
                    return redirect('training_program_list')

                # Kiểm tra xem TrainingProgram đã tồn tại chưa
                if not TrainingProgram.objects.filter(program_id=program_id).exists():
                    TrainingProgram.objects.create(
                        program_id=program_id,
                        program_name=program_name,
                        StartYear=int(start_year),
                        major=major  # Liên kết với Major
                    )

            messages.success(request, 'Dữ liệu đã được lưu thành công.')
        except Exception as e:
            messages.error(request, f'Đã xảy ra lỗi khi lưu dữ liệu: {e}')
        
        return redirect('training_program_list')

    return redirect('training_program_list')


# danh sach khoa hoc 
def list_of_courses(request):
    courses = Course.objects.all()
    context = {
        'title': 'Danh sách khóa học',
        'courses': courses
    }
    return render(request,'courses/course_list.html',context)

# Thêm/Sửa course 
def course_form(request, course_id=None):
    if course_id:
        course = get_object_or_404(Course, course_id=course_id)
    else:
        course = None
    
    form = CourseForm(request.POST or None, instance=course)
    if form.is_valid():
        form.save()
        return redirect('list_of_courses')
    
    return render(request, 'courses/course_form.html', {'form': form})
# xóa course
def course_delete(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('list_of_courses')
    
    context = {
        'title': 'Xóa Khóa học',
        'course': course,
    }
    return render(request, 'courses/course_delete.html', context)

# xử lý upload và xem trước 
def import_courses(request):
    if request.method == 'POST' and 'file' in request.FILES:
        csv_file = request.FILES['file']

        # Kiểm tra định dạng file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File không đúng định dạng CSV.')
            return redirect('list_of_courses')

        try:
            # Đọc dữ liệu từ file CSV
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            # Chuẩn bị dữ liệu xem trước
            data_preview = [
                {
                    'course_id': row.get('course_id'),
                    'course_name': row.get('course_name'),
                    'credits': row.get('credits'),
                    'theory_hours': row.get('theory_hours'),
                    'practice_hours': row.get('practice_hours'),
                    'prerequisites': row.get('prerequisites'),
                }
                for row in reader
            ]

            return render(request, 'courses/import_courses_preview.html', {'data_preview': data_preview})

        except Exception as e:
            messages.error(request, f'Đã xảy ra lỗi: {e}')
            return redirect('list_of_courses')

    return redirect('list_of_courses')

# xử lý lưu vào cơ sở dữ liệu
def confirm_courses(request):
    if request.method == 'POST':
        course_ids = request.POST.getlist('course_id')
        course_names = request.POST.getlist('course_name')
        credits = request.POST.getlist('credits')
        theory_hours = request.POST.getlist('theory_hours')
        practice_hours = request.POST.getlist('practice_hours')
        prerequisites = request.POST.getlist('prerequisites')

        for course_id, course_name, credits,theory_hours,practice_hours,prerequisites in zip(course_ids, course_names, credits,theory_hours,practice_hours,prerequisites):
            if not Course.objects.filter(course_id=course_id).exists():
                course = Course.objects.create(
                    course_id=course_id,
                    course_name=course_name,
                    credits=int(credits),
                    theory_hours=int(theory_hours),
                    practice_hours=int(practice_hours),
                )
                 # Xử lý prerequisites
                if prerequisites:
                    prerequisite_ids = prerequisites.split(',')
                    prerequisite_courses = Course.objects.filter(course_id__in=prerequisite_ids)
                    course.prerequisites.set(prerequisite_courses)

                course.save()

        messages.success(request, 'Dữ liệu đã được lưu thành công.')
        return redirect('training_program_list')

    return redirect('list_of_courses')

def list_of_course_training_program(request):
    course_training_programs = CourseTrainingProgram.objects.all()
    return render(request, 'course_trainprogram/list_of_course_training_program.html', {'course_training_programs': course_training_programs})

def import_courses_program(request):
    if request.method == 'POST' and 'file' in request.FILES:
        csv_file = request.FILES['file']

        #kiem tra dinh dang file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Vui lòng chọn file CSV')
            return redirect('list_of_course_training_program')
        
        try:
            #doc du lieu tu file csv
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            # chuan bi du lieu xem truoc
            data_preview = [
                {
                    'semester': row.get('semester'),
                    'course_type':row.get('course_type'),
                    'program_id':row.get('program_id'),
                    'course_id':row.get('course_id'),
                }
                for row in reader
            ]
            # print(data_preview)
            return render(request, 'course_trainprogram/import_course_training_preview.html', {'data_preview': data_preview})
    
        except Exception as e:
            messages.error(request, f'Đã xảy ra lỗi: {e}')
            return redirect('list_of_course_training_program')
    return redirect('list_of_course_training_program')     
def confirm_courses_program(request):
    if request.method == 'POST':
        print(f"POST data: {request.POST}")
        
        course_types = request.POST.getlist('course_type')
        semesters = request.POST.getlist('semester')
        program_ids = request.POST.getlist('program_id')
        course_ids = request.POST.getlist('course_id')

        # Kiểm tra dữ liệu nhận được
        print(f"course_types: {course_types}")
        print(f"semesters: {semesters}")
        print(f"program_ids: {program_ids}")
        print(f"course_ids: {course_ids}")

        # Duyệt qua từng bộ dữ liệu và tạo CourseTrainingProgram
        for course_type, semester, program_id, course_id in zip(course_types, semesters, program_ids, course_ids):
            # Kiểm tra xem có đối tượng tương ứng hay không
            if not CourseTrainingProgram.objects.filter(course__course_id=course_id, program__program_id=program_id).exists():
                course_train = CourseTrainingProgram(
                    course_type=course_type,
                    semester=semester,
                )
                
                # Lấy các đối tượng Course và TrainingProgram
                course = Course.objects.get(course_id=course_id)
                program = TrainingProgram.objects.get(program_id=program_id)

                # Gán mối quan hệ
                course_train.course = course
                course_train.program = program
                course_train.save()

                print(f"Đã lưu: {course_train}")

        messages.success(request, 'Dữ liệu đã được lưu thành công.')
        return redirect('list_of_course_training_program')

    return redirect('list_of_course_training_program')

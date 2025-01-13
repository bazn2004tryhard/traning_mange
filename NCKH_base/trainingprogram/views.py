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
            data_preview = [
                {
                    'program_id': row.get('program_id'),
                    'program_name': row.get('program_name'),
                    'StartYear': row.get('StartYear'),
                }
                for row in reader
            ]

            return render(request, 'trainingprogram/import_preview.html', {'data_preview': data_preview})

        except Exception as e:
            messages.error(request, f'Đã xảy ra lỗi: {e}')
            return redirect('training_program_list')

    return redirect('training_program_list')

# xử lý lưu vào cơ sở dữ liệu
def confirm_import_training_program(request):
    if request.method == 'POST':
        program_ids = request.POST.getlist('program_id')
        program_names = request.POST.getlist('program_name')
        start_years = request.POST.getlist('StartYear')

        for program_id, program_name, start_year in zip(program_ids, program_names, start_years):
            if not TrainingProgram.objects.filter(program_id=program_id).exists():
                TrainingProgram.objects.create(
                    program_id=program_id,
                    program_name=program_name,
                    StartYear=int(start_year)
                )

        messages.success(request, 'Dữ liệu đã được lưu thành công.')
        return redirect('training_program_list')

    return redirect('training_program_list')

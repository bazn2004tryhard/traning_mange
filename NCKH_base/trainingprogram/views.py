from django.shortcuts import render

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
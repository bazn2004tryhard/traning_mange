from django.contrib import admin
from .models import TrainingProgram, Course, CourseTrainingProgram, Major, Faculty, OptionalGroup

class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_name', 'credits', 'get_prerequisites')

class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ('program_id', 'program_name', 'StartYear', 'get_major')  # Sử dụng phương thức get_major()

class CourseTrainingProgramAdmin(admin.ModelAdmin):
    list_display = ('program', 'course', 'semester', 'course_type')

class MajorAdmin(admin.ModelAdmin):
    list_display = ('major_id', 'major_name', 'get_faculty')  # Sử dụng phương thức get_faculty()

class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'faculty_name', 'Phone', 'Email', 'Address')

admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Major, MajorAdmin)
admin.site.register(TrainingProgram, TrainingProgramAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseTrainingProgram, CourseTrainingProgramAdmin)

from django.contrib import admin

# Register your models here.
from .models import TrainingProgram, Course, CourseTrainingProgram
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_name','credits','get_prerequisites')

class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ('program_id', 'program_name','StartYear')


admin.site.register(TrainingProgram, TrainingProgramAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseTrainingProgram)
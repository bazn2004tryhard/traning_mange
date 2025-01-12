from django import forms
from .models import TrainingProgram, Course, CourseTrainingProgram

class TrainingProgramForm(forms.ModelForm):
    class Meta:
        model = TrainingProgram
        fields = '__all__'

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
class CourseTrainingProgramForm(forms.ModelForm):
    class Meta:
        model = CourseTrainingProgram
        fields = '__all__'
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
        widgets = {
            'course_id': forms.TextInput(attrs={'class': 'form-control'}),
            'course_name': forms.TextInput(attrs={'class': 'form-control'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control'}),
            'theory_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'practice_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'prerequisites': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
class CourseTrainingProgramForm(forms.ModelForm):
    class Meta:
        model = CourseTrainingProgram
        fields = '__all__'
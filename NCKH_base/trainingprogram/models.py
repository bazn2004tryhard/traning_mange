from django.db import models

# Create your models here.
class TrainingProgram(models.Model):
    program_id = models.CharField(max_length=255,primary_key=True)
    program_name = models.CharField(max_length=255)
    StartYear = models.IntegerField()

    def __str__(self):
        return self.program_name

class Course(models.Model):
    course_id = models.CharField(max_length=255, primary_key=True)
    course_name = models.CharField(max_length=255)
    credits = models.IntegerField()
    theory_hours = models.IntegerField()
    practice_hours = models.IntegerField()
    project_hours = models.IntegerField(default=0)
    prerequisites = models.ManyToManyField('self', symmetrical=False, related_name='prerequisite_for', blank=True)

    def __str__(self):
        return self.course_name
    def get_prerequisites(self):  
        return ", ".join([prerequisite.course_name for prerequisite in self.prerequisites.all()]) or "None"    
class CourseTrainingProgram(models.Model):
    C_TYPE =(
        ('0','0'),
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ('8','8'),
        ('9','9'),
    )
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.IntegerField() 
    course_type = models.IntegerField( 
        choices=C_TYPE
        )

    def __str__(self):
        return f"{self.program.program_name} - {self.course.course_name}"
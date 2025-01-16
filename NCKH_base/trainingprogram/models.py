from django.db import models

# Create your models here.
class Faculty(models.Model):
    faculty_id = models.CharField(max_length=255, primary_key=True)
    faculty_name = models.CharField(max_length=255)
    Phone = models.CharField(max_length=255, blank=True, null=True)
    Email = models.EmailField(max_length=255, blank=True, null=True)
    Address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.faculty_name

class Major(models.Model):
    major_id = models.CharField(max_length=255, primary_key=True)
    major_name = models.CharField(max_length=255)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.major_name

    @property
    def get_faculty(self):
        return self.faculty

class TrainingProgram(models.Model):
    program_id = models.CharField(max_length=255, primary_key=True)
    program_name = models.CharField(max_length=255)
    StartYear = models.IntegerField()
    major = models.ForeignKey(Major, on_delete=models.CASCADE)

    def __str__(self):
        return self.program_name

    @property
    def get_major(self):
        return self.major

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
    C_TYPE = (
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
    )
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.IntegerField()
    course_type = models.IntegerField(choices=C_TYPE)

    def __str__(self):
        return f"{self.program.program_name} - {self.course.course_name}"

class OptionalGroup(models.Model):
    course_type = models.IntegerField(primary_key=True)  # Đặt course_type làm khóa chính
    group_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='optional_groups')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='optional_groups')

    def __str__(self):
        return self.group_name

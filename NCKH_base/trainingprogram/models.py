from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

# Create your models here.
class Faculty(models.Model):
    faculty_id = models.CharField(max_length=255, primary_key=True)
    # faculty_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    faculty_name = models.CharField(max_length=255)
    Phone = models.CharField(max_length=255, blank=True, null=True)
    Email = models.EmailField(max_length=255, blank=True, null=True)
    Address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.faculty_id

class Major(models.Model):
    major_id = models.CharField(max_length=255, primary_key=True)
    major_name = models.CharField(max_length=255)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.major_id

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
    def get_program(self):
        return self.program.program_id
    def get_course(self):
        return self.course.course_id

# Bảng Role
class Role(models.Model):
    RoleID = models.BigAutoField(primary_key=True)  # PK
    RoleName = models.CharField(max_length=255)
    Create_at = models.DateField(auto_now_add=True)
    Update_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.RoleID

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Custom manager cho User
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username must be provided")
        # Tạo đối tượng user
        user = self.model(username=username, **extra_fields)
        user.set_password(password)  # Sử dụng set_password để mã hóa mật khẩu
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        # Đặt các cờ mặc định cho superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(username, password, **extra_fields)

# Bảng User
class User(AbstractBaseUser, PermissionsMixin):
    # UserID = models.CharField(max_length=255, primary_key=True)  # PK
    UserID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    # password = models.CharField(max_length=255)  # Lưu mật khẩu đã mã hóa
    img_url = models.CharField(max_length=255, blank=True, null=True)
    Create_at = models.DateField(auto_now_add=True)
    Update_at = models.DateField(auto_now=True)
    email = models.EmailField(unique=True, null=True, blank=True) 

    # Các cờ bắt buộc cho authentication
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # is_superuser đã được cung cấp bởi PermissionsMixin

    # Khóa ngoại
    faculty = models.ForeignKey("Faculty", on_delete=models.SET_NULL, null=True, blank=True)
    # lecturer = models.ForeignKey("Lecturer", on_delete=models.SET_NULL, null=True, blank=True)
    # student = models.ForeignKey("Student", on_delete=models.SET_NULL, null=True, blank=True)

    # Chỉ định trường dùng để đăng nhập
    USERNAME_FIELD = 'username'
    # Danh sách các trường bắt buộc khi tạo superuser (ngoài USERNAME_FIELD và password)
    REQUIRED_FIELDS = ['email']

    # Gán manager
    objects = CustomUserManager()

    def __str__(self):
        return self.username

    @property
    def get_faculty(self):
        return self.faculty.faculty_id

    @property
    def get_student(self):
        return self.student.StudentID
    
    @property
    def get_lecturer(self):
        return self.lecturer.LecturerID

# Bảng UserRole (Bảng trung gian User - Role)
class UserRole(models.Model):
    UserID = models.ForeignKey(User, on_delete=models.CASCADE)  # FK
    RoleID = models.ForeignKey(Role, on_delete=models.CASCADE)  # FK

    class Meta:
        unique_together = ('UserID', 'RoleID')  # Đảm bảo mỗi User chỉ có một vai trò duy nhất

# Bảng Lecturer
class Lecturer(models.Model):
    LecturerID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # PK
    Expertise = models.CharField(max_length=255)
    AcademicTitle = models.CharField(max_length=255)
    Fullname = models.CharField(max_length=255)
    Email = models.CharField(max_length=255)
    Phone = models.CharField(max_length=255)
    Gender = models.CharField(max_length=255)

    # Khóa ngoại
    faculty = models.ForeignKey("Faculty", on_delete=models.CASCADE)  # FK
    def __str__(self):
        return self.LecturerID
    @property
    def get_faculty(self):
        return self.faculty.faculty_id

# Bảng Student
class Student(models.Model):
    StudentID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # PK
    AcademicYear = models.CharField(max_length=255,null=True)
    Class = models.CharField(max_length=255,null=True)
    Fullname = models.CharField(max_length=255,null=True)
    Dob = models.DateField(null=True)
    Gender = models.CharField(max_length=255,null=True)
    Address = models.CharField(max_length=255,null=True)
    Email = models.CharField(max_length=255,null=True)
    Phone = models.CharField(max_length=255,null=True)

    # Khóa ngoại
    major = models.ForeignKey("Major", on_delete=models.CASCADE, null=True)  # FK
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name='student', null=True)

    def __str__(self):
        return str(self.StudentID)

    @property
    def get_major(self):
        return self.major.major_id

class Grade(models.Model):
    # GradeID = models.CharField(max_length=255, primary_key=True)
    GradeID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ContinuosAssScore = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], null=True)
    FinalExamScore = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], null=True)
    Result =  models.CharField(max_length=255, null=True)
    Semester = models.CharField(max_length=255, null=True) # Semester này phải tự động lấy
    AcademyYear = models.CharField(max_length=255, null=True) # Đây cũng thế, tạm thời cho null = True để giải quyết
    TestTime = models.CharField(max_length=255, null=True)
    
    #khoa ngoai
    student = models.ForeignKey("Student", on_delete=models.CASCADE)  # FK
    course = models.ForeignKey("Course",on_delete=models.CASCADE)

    def __str__(self):
        return str(self.GradeID)
    def get_student(self):
        return self.student.StudentID
    def get_course(self):
        return self.course.course_id
    
# Bảng kì
class Semester(models.Model):
    ID = models.CharField(max_length= 255, primary_key= True)
    SemesterName = models.CharField(max_length= 255)
    StartDate = models.DateField(null=True)
    EndDate = models.DateField(null=True)

# Bảng trung gian kì và học sinh: Bảng đánh giá
class Evaluate(models.Model):
    ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    semester = models.ForeignKey("Semester", on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    TrainingPoint = models.IntegerField()
    
    def get_student(self):
        return self.student.StudentID
    def get_semester(self):
        return self.semester.ID
    
    
class Class(models.Model):
    ClassID = models.CharField(max_length=255, primary_key=True)
    Classroom =  models.CharField(max_length=255)
    AcademyYear = models.CharField(max_length=255)
    Semester = models.CharField(max_length=255)
    LecturerID =  models.CharField(max_length=255)
    # khóa ngoai
    course = models.ForeignKey("Course",on_delete=models.CASCADE)

    def __str__(self):
        return self.ClassID
    def get_course(self):
        return self.course.course_id

class ClassSchedule(models.Model):
    ScheduleID = models.CharField(max_length=255, primary_key=True)
    Date = models.DateField()
    StartTime = models.TimeField()
    EndTime = models.TimeField()
    Classroom =  models.CharField(max_length=255)
    #khoa ngoai
    class_id = models.ForeignKey("Class",on_delete=models.CASCADE)

    def __str__(self):
        return self.ScheduleID
    def get_class(self):
        return self.class_id.ClassID

class Enrollment(models.Model):
    C_TYPE = (
        ('Da Dang Ky', 'Đã đăng ký'),
        ('Dang Cho Duyet', 'Đang chờ duyệt'),
        ('Da Huy Dang Ky', 'Đã hủy đăng ký'),
        ('Dang Huy Dang Ky', 'Đang hủy đăng ký'),
    )
    EnrollmentID = models.CharField(max_length=255, primary_key=True)
    EnrollDate = models.DateField()
    Status = models.CharField(max_length=20, choices=C_TYPE)
    StudentID = models.CharField(max_length=255)
    # khóa ngoai
    class_id = models.ForeignKey("Class",on_delete=models.CASCADE)

    def __str__(self):
        return self.EnrollmentID
    def get_class(self):
        return self.class_id.ClassID
class RegistrationHistory(models.Model):
   C_TYPE =(
       ('Dang Ky', 'Đăng ký'),
       ('Huy Dang Ky', 'Hủy đăng ký'),
   )
   HistoryID = models.CharField(max_length=255,primary_key=True)
   TimeStamp = models.TimeField()
   Action = models.CharField(max_length=20, choices=C_TYPE)
   StudentID = models.CharField(max_length=255)
   ClassID = models.CharField(max_length=255)

   #khoa ngoai
   enrollment = models.ForeignKey("Enrollment",on_delete=models.CASCADE)
   def __str__(self):
       return self.HistoryID
   def get_enrollment(self):
       return self.enrollment.EnrollmentID
    
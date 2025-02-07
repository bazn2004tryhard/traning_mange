from django.contrib import admin
from .models import TrainingProgram, Course, CourseTrainingProgram, Major, Faculty, OptionalGroup,Role,User,UserRole,Lecturer,Student,Grade,Class,ClassSchedule,Enrollment,RegistrationHistory

class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_name', 'credits', 'get_prerequisites')
class OptionalGroupAdmin(admin.ModelAdmin):
    list_display = ('course_type', 'group_name','description','get_program','get_course')
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ('program_id', 'program_name', 'StartYear', 'get_major')  # Sử dụng phương thức get_major()

class CourseTrainingProgramAdmin(admin.ModelAdmin):
    list_display = ('program', 'course', 'semester', 'course_type')

class MajorAdmin(admin.ModelAdmin):
    list_display = ('major_id', 'major_name', 'get_faculty')  # Sử dụng phương thức get_faculty()

class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'faculty_name', 'Phone', 'Email', 'Address')
class RoleAdmin(admin.ModelAdmin):
    list_display = ('RoleID', 'RoleName','Create_at','Update_at')
class UserAdmin(admin.ModelAdmin):
    list_display = ('UserID','username','password','img_url','Create_at','Update_at','get_faculty','get_lecturer','get_student')
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('UserID','RoleID')
class LecturerAdmin(admin.ModelAdmin):
    list_display = ('LecturerID','Expertise','AcademicTitle','Fullname','Email','Phone','Gender','get_faculty')
class StudentAdmin(admin.ModelAdmin):
    list_display = ('StudentID','AcademicYear','Class','Fullname','Dob','Gender','Address','Email','Phone','get_major')
class GradeAdmin(admin.ModelAdmin):
    list_display = ('GradeID','ContinuosAssScore','FinalExamScore','Result','Semester','AcademyYear','get_student','get_course')
class ClassAdmin(admin.ModelAdmin):
    list_display = ('ClassID','Classroom','AcademyYear','Semester','LecturerID','get_course')
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('ScheduleID','Date','StartTime','EndTime','Classroom','get_class')
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('EnrollmentID','EnrollDate','Status','StudentID','get_class')
class RegistrationHistoryAdmin(admin.ModelAdmin):
    list_display = ('HistoryID','TimeStamp','Action','StudentID','ClassID','get_enrollment')
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Major, MajorAdmin)
admin.site.register(TrainingProgram, TrainingProgramAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseTrainingProgram, CourseTrainingProgramAdmin)
admin.site.register(Role,RoleAdmin)
admin.site.register(User,UserAdmin)
admin.site.register(UserRole,UserRoleAdmin)
admin.site.register(Lecturer,LecturerAdmin)
admin.site.register(Student,StudentAdmin)
admin.site.register(Grade,GradeAdmin)
admin.site.register(Class,ClassAdmin)
admin.site.register(ClassSchedule,ClassScheduleAdmin)
admin.site.register(Enrollment,EnrollmentAdmin)
admin.site.register(RegistrationHistory,RegistrationHistoryAdmin)
admin.site.register(OptionalGroup,OptionalGroupAdmin)
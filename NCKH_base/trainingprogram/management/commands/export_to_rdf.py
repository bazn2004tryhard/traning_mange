'''
python manage.py export_to_rdf
'''

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD
from datetime import date, time  # Để xử lý kiểu dữ liệu date/time

# Import các models Django của bạn
# Giả sử các models của bạn nằm trong app 'your_app_name'
# Thay 'your_app_name' bằng tên app thực tế của bạn
from trainingprogram.models import (
    Faculty, Major, TrainingProgram, Course, OptionalGroup,
    CourseTrainingProgram, User, Student, Grade, Semester as AcademicTermModel
    # Đổi tên Semester thành AcademicTermModel để tránh trùng với rdflib.Semester (nếu có)
    # Hoặc sử dụng tên đầy đủ khi gọi
)

# Định nghĩa Namespace cho ontology của bạn
UNI = Namespace("http://www.semanticweb.org/admin/ontologies/2025/4/university-ontology-31#")


# Hàm trợ giúp để tạo URI an toàn
def safe_uri_component(text):
    if text is None:
        return "None"
    return str(text).replace(" ", "_").replace("/", "-").replace(":", "_")


class Command(BaseCommand):
    help = 'Exports university data from database to an RDF file based on the university ontology.'

    def handle(self, *args, **options):
        g = Graph()
        g.bind("uni", UNI)  # Bind prefix cho namespace

        self.stdout.write(self.style.SUCCESS("Starting RDF export..."))

        # 1. Faculties
        self.stdout.write("Processing Faculties...")
        for faculty_obj in Faculty.objects.all():
            faculty_uri = UNI[f"Faculty_{safe_uri_component(faculty_obj.faculty_id)}"]
            g.add((faculty_uri, RDF.type, UNI.Faculty))
            g.add((faculty_uri, UNI.facultyID, Literal(faculty_obj.faculty_id, datatype=XSD.string)))
            g.add((faculty_uri, UNI.facultyName, Literal(faculty_obj.faculty_name, datatype=XSD.string)))
            if faculty_obj.Phone:
                g.add((faculty_uri, UNI.facultyPhone, Literal(faculty_obj.Phone, datatype=XSD.string)))
            if faculty_obj.Email:
                g.add((faculty_uri, UNI.facultyEmail, Literal(faculty_obj.Email, datatype=XSD.string)))
            if faculty_obj.Address:
                g.add((faculty_uri, UNI.facultyAddress, Literal(faculty_obj.Address, datatype=XSD.string)))
        self.stdout.write(self.style.SUCCESS(f"Processed {Faculty.objects.count()} Faculties."))

        # 2. Majors
        self.stdout.write("Processing Majors...")
        for major_obj in Major.objects.all():
            major_uri = UNI[f"Major_{safe_uri_component(major_obj.major_id)}"]
            g.add((major_uri, RDF.type, UNI.Major))
            g.add((major_uri, UNI.majorID, Literal(major_obj.major_id, datatype=XSD.string)))
            g.add((major_uri, UNI.majorName, Literal(major_obj.major_name, datatype=XSD.string)))
            if major_obj.faculty:
                faculty_uri_ref = UNI[f"Faculty_{safe_uri_component(major_obj.faculty.faculty_id)}"]
                g.add((major_uri, UNI.belongsToFaculty, faculty_uri_ref))
                g.add((faculty_uri_ref, UNI.hasMajor, major_uri))  # Inverse property
        self.stdout.write(self.style.SUCCESS(f"Processed {Major.objects.count()} Majors."))

        # 3. Training Programs
        self.stdout.write("Processing Training Programs...")
        for tp_obj in TrainingProgram.objects.all():
            tp_uri = UNI[f"TrainingProgram_{safe_uri_component(tp_obj.program_id)}"]
            g.add((tp_uri, RDF.type, UNI.TrainingProgram))
            g.add((tp_uri, UNI.programID, Literal(tp_obj.program_id, datatype=XSD.string)))
            g.add((tp_uri, UNI.programName, Literal(tp_obj.program_name, datatype=XSD.string)))
            if tp_obj.StartYear:
                g.add((tp_uri, UNI.startYear, Literal(str(tp_obj.StartYear), datatype=XSD.gYear)))
            if tp_obj.major:
                major_uri_ref = UNI[f"Major_{safe_uri_component(tp_obj.major.major_id)}"]
                g.add((tp_uri, UNI.offeredByMajor, major_uri_ref))
                g.add((major_uri_ref, UNI.offersTrainingProgram, tp_uri))  # Inverse
        self.stdout.write(self.style.SUCCESS(f"Processed {TrainingProgram.objects.count()} Training Programs."))

        # 4. Courses
        self.stdout.write("Processing Courses...")
        for course_obj in Course.objects.all():
            course_uri = UNI[f"Course_{safe_uri_component(course_obj.course_id)}"]
            g.add((course_uri, RDF.type, UNI.Course))
            g.add((course_uri, UNI.courseID, Literal(course_obj.course_id, datatype=XSD.string)))
            g.add((course_uri, UNI.courseName, Literal(course_obj.course_name, datatype=XSD.string)))
            g.add((course_uri, UNI.credits, Literal(course_obj.credits, datatype=XSD.integer)))
            g.add((course_uri, UNI.theoryHours, Literal(course_obj.theory_hours, datatype=XSD.integer)))
            g.add((course_uri, UNI.practiceHours, Literal(course_obj.practice_hours, datatype=XSD.integer)))
            g.add((course_uri, UNI.projectHours, Literal(course_obj.project_hours, datatype=XSD.integer)))
            for prereq in course_obj.prerequisites.all():
                prereq_uri = UNI[f"Course_{safe_uri_component(prereq.course_id)}"]
                g.add((course_uri, UNI.hasPrerequisite, prereq_uri))
                g.add((prereq_uri, UNI.isPrerequisiteFor, course_uri))  # Inverse
        self.stdout.write(self.style.SUCCESS(f"Processed {Course.objects.count()} Courses."))

        # 5. Optional Groups
        self.stdout.write("Processing Optional Groups...")
        for og_obj in OptionalGroup.objects.all():
            # Sử dụng og_obj.id (UUID) cho URI
            og_uri = UNI[f"OptionalGroup_{safe_uri_component(str(og_obj.id))}"]
            g.add((og_uri, RDF.type, UNI.OptionalGroup))
            g.add((og_uri, UNI.optionalGroupID, Literal(str(og_obj.id), datatype=XSD.string)))  # Ontology dùng string
            g.add((og_uri, UNI.optionalGroupName, Literal(og_obj.group_name, datatype=XSD.string)))
            if og_obj.description:
                g.add((og_uri, UNI.optionalGroupDescription, Literal(og_obj.description, datatype=XSD.string)))
            if og_obj.min_credits is not None:
                g.add((og_uri, UNI.minCreditsRequired, Literal(og_obj.min_credits, datatype=XSD.integer)))
        self.stdout.write(self.style.SUCCESS(f"Processed {OptionalGroup.objects.count()} Optional Groups."))

        # 6. Program Course Links
        self.stdout.write("Processing Program Course Links (CourseTrainingProgram)...")
        for ctp_obj in CourseTrainingProgram.objects.all():
            pcl_id = f"PCL_{ctp_obj.pk}"
            pcl_uri = UNI[safe_uri_component(pcl_id)]
            g.add((pcl_uri, RDF.type, UNI.ProgramCourseLink))
            g.add((pcl_uri, UNI.linkID, Literal(pcl_id, datatype=XSD.string)))

            if ctp_obj.semester is not None:
                g.add((pcl_uri, UNI.stipulatedSemester, Literal(ctp_obj.semester, datatype=XSD.integer)))

            req_type_str = "Optional" if ctp_obj.course_type == 1 else "Elective"
            if ctp_obj.course_type == 0: req_type_str = "Compulsory"

            g.add((pcl_uri, UNI.requirementType, Literal(req_type_str, datatype=XSD.string)))

            if ctp_obj.program:
                tp_uri_ref = UNI[f"TrainingProgram_{safe_uri_component(ctp_obj.program.program_id)}"]
                g.add((pcl_uri, UNI.linksProgram, tp_uri_ref))
                g.add((tp_uri_ref, UNI.hasProgramComponent, pcl_uri))  # Inverse

            if ctp_obj.course:
                course_uri_ref = UNI[f"Course_{safe_uri_component(ctp_obj.course.course_id)}"]
                g.add((pcl_uri, UNI.linksCourse, course_uri_ref))
                g.add((course_uri_ref, UNI.isComponentOfProgram, pcl_uri))  # Inverse

            if ctp_obj.option_G:
                og_uri_ref = UNI[f"OptionalGroup_{safe_uri_component(str(ctp_obj.option_G.id))}"]
                g.add((pcl_uri, UNI.partOfOptionalGroup, og_uri_ref))
                g.add((og_uri_ref, UNI.groupsProgramComponent, pcl_uri))  # Inverse
        self.stdout.write(
            self.style.SUCCESS(f"Processed {CourseTrainingProgram.objects.count()} Program Course Links."))

        # 7. User Accounts (từ User model)
        self.stdout.write("Processing User Accounts...")
        for user_obj in User.objects.all():
            user_acc_uri = UNI[f"UserAccount_{safe_uri_component(str(user_obj.UserID))}"]
            g.add((user_acc_uri, RDF.type, UNI.UserAccount))
            g.add((user_acc_uri, UNI.accountID, Literal(str(user_obj.UserID), datatype=XSD.string)))
            g.add((user_acc_uri, UNI.username, Literal(user_obj.username, datatype=XSD.string)))
            if user_obj.email:
                g.add((user_acc_uri, UNI.accountEmail, Literal(user_obj.email, datatype=XSD.string)))
            if user_obj.img_url:
                g.add((user_acc_uri, UNI.userImageUrl,
                       Literal(user_obj.img_url, datatype=XSD.string)))  # Giả sử XSD.string là phù hợp
            g.add((user_acc_uri, UNI.isActive, Literal(user_obj.is_active, datatype=XSD.boolean)))
            g.add((user_acc_uri, UNI.isStaff, Literal(user_obj.is_staff, datatype=XSD.boolean)))
            g.add((user_acc_uri, UNI.isSuperuser, Literal(user_obj.is_superuser, datatype=XSD.boolean)))
            if isinstance(user_obj.Create_at, date):  # dateJoined trong ontology
                g.add((user_acc_uri, UNI.dateJoined, Literal(user_obj.Create_at.isoformat(), datatype=XSD.date)))

            if user_obj.faculty:
                faculty_uri_ref = UNI[f"Faculty_{safe_uri_component(user_obj.faculty.faculty_id)}"]
                g.add((user_acc_uri, UNI.accountAffiliatedWithFaculty, faculty_uri_ref))
                g.add((faculty_uri_ref, UNI.hasAffiliatedUser, user_acc_uri))  # Inverse
        self.stdout.write(self.style.SUCCESS(f"Processed {User.objects.count()} User Accounts."))

        # 8. Students
        self.stdout.write("Processing Students...")
        for student_obj in Student.objects.all():
            student_uri = UNI[f"Student_{safe_uri_component(str(student_obj.StudentID))}"]
            g.add((student_uri, RDF.type, UNI.Student))
            g.add((student_uri, UNI.studentID, Literal(str(student_obj.StudentID), datatype=XSD.string)))
            if student_obj.Fullname:
                g.add((student_uri, UNI.studentFullName, Literal(student_obj.Fullname, datatype=XSD.string)))
            if student_obj.Email:
                g.add((student_uri, UNI.studentEmail, Literal(student_obj.Email, datatype=XSD.string)))
            if student_obj.Phone:
                g.add((student_uri, UNI.studentPhone, Literal(student_obj.Phone, datatype=XSD.string)))
            if student_obj.Gender:
                g.add((student_uri, UNI.studentGender, Literal(student_obj.Gender, datatype=XSD.string)))
            if student_obj.Address:
                g.add((student_uri, UNI.studentAddress, Literal(student_obj.Address, datatype=XSD.string)))
            if student_obj.AcademicYear:  # academicEnrollmentYear trong ontology
                g.add((student_uri, UNI.academicEnrollmentYear,
                       Literal(student_obj.AcademicYear, datatype=XSD.string)))  # Ontology mong đợi string?
            if student_obj.Class:  # className trong ontology
                g.add((student_uri, UNI.className, Literal(student_obj.Class, datatype=XSD.string)))
            if student_obj.Dob and isinstance(student_obj.Dob, date):
                g.add((student_uri, UNI.dateOfBirth, Literal(student_obj.Dob.isoformat(), datatype=XSD.date)))

            if student_obj.major:
                major_uri_ref = UNI[f"Major_{safe_uri_component(student_obj.major.major_id)}"]
                g.add((student_uri, UNI.studiesMajor, major_uri_ref))
                g.add((major_uri_ref, UNI.hasEnrolledStudent, student_uri))  # Inverse

            if hasattr(student_obj, 'user') and student_obj.user:  # Check if user relationship exists and is not None
                user_acc_uri_ref = UNI[f"UserAccount_{safe_uri_component(str(student_obj.user.UserID))}"]
                g.add((student_uri, UNI.hasUserAccount, user_acc_uri_ref))
                g.add((user_acc_uri_ref, UNI.isAccountOfStudent, student_uri))  # Inverse
        self.stdout.write(self.style.SUCCESS(f"Processed {Student.objects.count()} Students."))

        # 9. Academic Terms (từ Semester model của Django)
        self.stdout.write("Processing Academic Terms...")
        for term_obj in AcademicTermModel.objects.all():  # Sử dụng AcademicTermModel đã đổi tên
            # Tạo term_id an toàn từ ID của model Semester
            term_id_safe = safe_uri_component(term_obj.ID)
            term_uri = UNI[f"AcademicTerm_{term_id_safe}"]
            g.add((term_uri, RDF.type, UNI.AcademicTerm))
            g.add((term_uri, UNI.termID, Literal(term_obj.ID, datatype=XSD.string)))
            g.add((term_uri, UNI.termName, Literal(term_obj.SemesterName, datatype=XSD.string)))
            if term_obj.StartDate and isinstance(term_obj.StartDate, date):
                g.add((term_uri, UNI.termStartDate, Literal(term_obj.StartDate.isoformat(), datatype=XSD.date)))
            if term_obj.EndDate and isinstance(term_obj.EndDate, date):
                g.add((term_uri, UNI.termEndDate, Literal(term_obj.EndDate.isoformat(), datatype=XSD.date)))
        self.stdout.write(self.style.SUCCESS(f"Processed {AcademicTermModel.objects.count()} Academic Terms."))

        # 10. Grades
        self.stdout.write("Processing Grades...")
        for grade_obj in Grade.objects.all():
            grade_uri = UNI[f"Grade_{safe_uri_component(str(grade_obj.GradeID))}"]
            g.add((grade_uri, RDF.type, UNI.Grade))
            g.add((grade_uri, UNI.gradeID, Literal(str(grade_obj.GradeID), datatype=XSD.string)))
            if grade_obj.ContinuosAssScore is not None:
                g.add((grade_uri, UNI.continuousAssessmentScore,
                       Literal(grade_obj.ContinuosAssScore, datatype=XSD.float)))
            if grade_obj.FinalExamScore is not None:
                g.add((grade_uri, UNI.finalExamScore, Literal(grade_obj.FinalExamScore, datatype=XSD.float)))
            if grade_obj.Result:
                g.add((grade_uri, UNI.gradeResult, Literal(grade_obj.Result, datatype=XSD.string)))

            # Tạo term_id từ grade_obj.Semester và grade_obj.AcademyYear để tham chiếu AcademicTerm
            # Giả sử ID của AcademicTermModel (Django Semester model) có dạng "HK1_2023-2024"
            # Bạn cần đảm bảo logic này khớp với cách bạn tạo term_uri ở bước 9
            if grade_obj.Semester and grade_obj.AcademyYear:
                # Đây là một ví dụ, bạn cần điều chỉnh cho phù hợp với cấu trúc ID của Semester model
                term_id_from_grade = f"{safe_uri_component(grade_obj.Semester)}_{safe_uri_component(grade_obj.AcademyYear)}"
                # Nếu ID của model Semester không theo format này, bạn cần query AcademicTermModel
                # Ví dụ: term_instance = AcademicTermModel.objects.filter(SemesterName=grade_obj.Semester, ...).first()
                # và lấy term_instance.ID
                # Dưới đây là giả định đơn giản, có thể cần điều chỉnh:
                # Tìm AcademicTerm dựa trên thông tin từ Grade
                try:
                    # Cần logic tìm kiếm AcademicTerm chính xác hơn
                    # Ví dụ: tìm theo tên học kỳ và năm học
                    # Đây chỉ là ví dụ, bạn cần một cách đáng tin cậy để map
                    # Ví dụ: nếu grade_obj.Semester là tên (e.g., "Học kỳ 1") và grade_obj.AcademyYear là năm ("2023-2024")
                    # và AcademicTermModel có termName và một trường cho năm học riêng.
                    # Hoặc nếu grade_obj.Semester đã là ID của AcademicTermModel
                    term_instance = AcademicTermModel.objects.get(
                        ID=grade_obj.Semester)  # Giả sử grade_obj.Semester là ID
                    term_uri_ref = UNI[f"AcademicTerm_{safe_uri_component(term_instance.ID)}"]
                    g.add((grade_uri, UNI.awardedInTerm, term_uri_ref))
                    g.add((term_uri_ref, UNI.hasGradesAwarded, grade_uri))  # Inverse
                except AcademicTermModel.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"AcademicTerm not found for grade {grade_obj.GradeID} with semester ID {grade_obj.Semester}. Skipping awardedInTerm."))
                except AcademicTermModel.MultipleObjectsReturned:
                    self.stdout.write(self.style.WARNING(
                        f"Multiple AcademicTerms found for grade {grade_obj.GradeID} with semester ID {grade_obj.Semester}. Skipping awardedInTerm."))

            if grade_obj.Semester:  # Ontology có gradeAwardedInSemesterName
                g.add((grade_uri, UNI.gradeAwardedInSemesterName, Literal(grade_obj.Semester, datatype=XSD.string)))
            if grade_obj.AcademyYear:  # Ontology có gradeAwardedInAcademicYear
                g.add((grade_uri, UNI.gradeAwardedInAcademicYear, Literal(grade_obj.AcademyYear, datatype=XSD.string)))
            if grade_obj.TestTime:
                g.add((grade_uri, UNI.testTime,
                       Literal(grade_obj.TestTime, datatype=XSD.string)))  # Hoặc XSD.time nếu format phù hợp

            if grade_obj.student:
                student_uri_ref = UNI[f"Student_{safe_uri_component(str(grade_obj.student.StudentID))}"]
                g.add((grade_uri, UNI.achievedByStudent, student_uri_ref))
                g.add((student_uri_ref, UNI.hasAchievedGrade, grade_uri))  # Inverse

            if grade_obj.course:
                course_uri_ref = UNI[f"Course_{safe_uri_component(grade_obj.course.course_id)}"]
                g.add((grade_uri, UNI.forCourse, course_uri_ref))
                g.add((course_uri_ref, UNI.hasStudentGrade, grade_uri))  # Inverse
        self.stdout.write(self.style.SUCCESS(f"Processed {Grade.objects.count()} Grades."))

        # Lưu file RDF
        output_filename = "rdf_data/university_data.rdf"
        # Lưu vào thư mục gốc của project hoặc một thư mục data cụ thể
        output_path = os.path.join(settings.BASE_DIR, output_filename)

        try:
            g.serialize(destination=output_path, format="xml")  # hoặc "turtle", "n3", "nt"
            self.stdout.write(self.style.SUCCESS(f"Successfully exported RDF data to {output_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error serializing RDF graph: {e}"))
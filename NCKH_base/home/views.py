from django.shortcuts import render
from trainingprogram.models import User, Course, Student, Grade, TrainingProgram, CourseTrainingProgram, OptionalGroup

# Create your views here.

def home(request):
    return render(request, 'home/home.html')


def placeholder_view(request, feature_name=None):
    page_title = "Sắp ra mắt"

    if feature_name:
        processed_name = feature_name.replace('-', ' ').replace('_', ' ')
        display_feature_name = processed_name.title()
        message = f"Tính năng '{display_feature_name}' đang được xây dựng và sẽ sớm có mặt!"
        page_title = f"{display_feature_name} (Sắp ra mắt)"
    else:
        message = "Tính năng này hiện đang trong quá trình phát triển. Vui lòng quay lại sau!"
    context = {
        'message': message,
        'page_title': page_title,
    }

    return render(request, 'home/placeholder.html', context)

# Hien thi thong tin sinh vien
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from trainingprogram.models import Student # Giả sử models.py nằm cùng cấp với views.py

@login_required # Đảm bảo chỉ người dùng đã đăng nhập mới xem được
def student_profile_view(request):
    try:
        student_instance = request.user.student
    except Student.DoesNotExist:
        student_instance = None
    context = {
        'student': student_instance,
        'current_user': request.user
    }
    return render(request, 'student_portal/student_profile.html', context)






# Hien thi thong tin chương trình đào tạo sinh viên học
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings  # Để lấy SPARQL_ENDPOINT_URL
from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML  # Hoặc TURTLE, N3 tùy định dạng CONSTRUCT
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from collections import defaultdict
import re  # Để trích xuất năm

# Định nghĩa các namespace thường dùng
UNI = Namespace("http://www.semanticweb.org/admin/ontologies/2025/4/university-ontology-31#")


def get_sparql_results(query_string, result_format=JSON):
    """Hàm tiện ích để thực thi truy vấn SPARQL và trả về kết quả."""
    sparql = SPARQLWrapper(settings.SPARQL_ENDPOINT_URL)
    sparql.setQuery(query_string)
    sparql.setReturnFormat(result_format)
    try:
        results = sparql.query().convert()
        return results
    except Exception as e:
        print(f"Lỗi truy vấn SPARQL: {e}")
        print(f"Query: {query_string}")
        return None


def parse_sparql_binding(binding, var_name, var_type='literal'):
    """Hàm tiện ích để lấy giá trị từ một binding của kết quả SPARQL."""
    if var_name not in binding:
        return None
    if var_type == 'uri':
        return binding[var_name]['value']
    elif var_type == 'literal':
        return binding[var_name]['value']
    elif var_type == 'typed-literal':  # ví dụ xsd:integer, xsd:gYear
        return {
            'value': binding[var_name]['value'],
            'datatype': binding[var_name].get('datatype')
        }
    return None


@login_required
def student_curriculum_sparql_view(request):
    student_id = request.user.username  # Giả định username là studentID trong RDF
    student_info = None
    training_program_uri = None
    training_program_details = {}

    courses_by_semester = defaultdict(lambda: {
        'compulsory': [],
        'optional_grouped': defaultdict(list),
        'optional_individual': []
    })
    optional_groups_details = {}  # {group_uri: {name, min_credits, description}}
    all_courses_details = {}  # {course_uri: {id, name, credits, ..., prerequisites: [prereq_uri_1,...]}}

    # --- Bước 1 & 2: Tìm Major và TrainingProgram của sinh viên ---
    query_student_program = f"""
        PREFIX uni: <{UNI}>
        PREFIX rdf: <{RDF}>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?student ?studentFullName ?major ?majorName ?academicEnrollmentYear ?trainingProgram ?programID ?programName ?programStartYear ?facultyName
        WHERE {{
            ?userAccount uni:username "{student_id}" ;
                         uni:isAccountOfStudent ?student .
            ?student uni:studentFullName ?studentFullName ;
                     uni:studiesMajor ?major ;
                     uni:academicEnrollmentYear ?academicEnrollmentYear . # Ví dụ: "K62 (2022)"

            ?major uni:majorName ?majorName ;
                   uni:belongsToFaculty ?faculty ;
                   uni:offersTrainingProgram ?trainingProgram .

            ?faculty uni:facultyName ?facultyName .

            ?trainingProgram uni:programID ?programID ;
                             uni:programName ?programName ;
                             uni:startYear ?programStartYear . # xsd:gYear
        }}
    """
    results_student_program = get_sparql_results(query_student_program)

    selected_program_candidate = None
    if results_student_program and results_student_program["results"]["bindings"]:
        student_enroll_year_str = parse_sparql_binding(results_student_program["results"]["bindings"][0],
                                                       "academicEnrollmentYear")
        student_actual_start_year = None
        if student_enroll_year_str:
            match = re.search(r'\b(20\d{2})\b', student_enroll_year_str)
            if match:
                student_actual_start_year = int(match.group(1))

        # Lọc TrainingProgram phù hợp nhất
        best_program = None
        min_year_diff = float('inf')

        for binding in results_student_program["results"]["bindings"]:
            # Lần đầu gán thông tin sinh viên (chỉ cần 1 lần)
            if not student_info:
                student_info = {
                    'uri': parse_sparql_binding(binding, "student", "uri"),
                    'fullName': parse_sparql_binding(binding, "studentFullName"),
                    'majorName': parse_sparql_binding(binding, "majorName"),
                    'majorURI': parse_sparql_binding(binding, "major", "uri"),
                    'academicEnrollmentYear': student_enroll_year_str,
                    'facultyName': parse_sparql_binding(binding, "facultyName")
                }

            program_start_year_literal = parse_sparql_binding(binding, "programStartYear", "typed-literal")
            if program_start_year_literal:
                program_start_year = int(program_start_year_literal['value'])  # xsd:gYear là YYYY

                if student_actual_start_year:
                    if program_start_year <= student_actual_start_year:
                        year_diff = student_actual_start_year - program_start_year
                        if year_diff < min_year_diff:
                            min_year_diff = year_diff
                            best_program = binding
                        elif year_diff == min_year_diff and program_start_year > int(
                                parse_sparql_binding(best_program, "programStartYear", "typed-literal")[
                                    'value']):  # If same diff, prefer newer program
                            best_program = binding
                elif not best_program or program_start_year > int(
                        parse_sparql_binding(best_program, "programStartYear", "typed-literal")[
                            'value']):  # No student year, pick latest
                    best_program = binding

        if best_program:
            selected_program_candidate = best_program
            training_program_uri = parse_sparql_binding(selected_program_candidate, "trainingProgram", "uri")
            training_program_details = {
                'uri': training_program_uri,
                'id': parse_sparql_binding(selected_program_candidate, "programID"),
                'name': parse_sparql_binding(selected_program_candidate, "programName"),
                'startYear': parse_sparql_binding(selected_program_candidate, "programStartYear", "typed-literal")[
                    'value'],
                'majorName': student_info['majorName'],  # Lấy từ student_info
                'facultyName': student_info['facultyName']  # Lấy từ student_info
            }

    # --- Bước 3: Lấy chi tiết các môn học của chương trình đào tạo đã chọn ---
    if training_program_uri:
        # Sử dụng CONSTRUCT sẽ trả về một graph, cần rdflib để parse
        # Hoặc một SELECT phức tạp hơn để lấy tất cả dữ liệu dạng bảng
        # Ở đây, chúng ta thử với SELECT để dễ xử lý hơn trong ví dụ này

        query_program_components = f"""
            PREFIX uni: <{UNI}>
            PREFIX rdf: <{RDF}>
            PREFIX rdfs: <{RDFS}>

            SELECT DISTINCT
                ?programCourseLink ?stipulatedSemester ?requirementType
                ?course ?courseID ?courseName ?credits ?theoryHours ?practiceHours ?projectHours
                ?prerequisiteCourse ?prerequisiteCourseID ?prerequisiteCourseName
                ?optionalGroup ?optionalGroupID ?optionalGroupName ?minCreditsRequired ?optionalGroupDescription
            WHERE {{
                <{training_program_uri}> uni:hasProgramComponent ?programCourseLink .
                ?programCourseLink uni:stipulatedSemester ?stipulatedSemester ;
                                 uni:requirementType ?requirementType ;
                                 uni:linksCourse ?course .

                ?course uni:courseID ?courseID ;
                        uni:courseName ?courseName ;
                        uni:credits ?credits ;
                        uni:theoryHours ?theoryHours ;
                        uni:practiceHours ?practiceHours ;
                        uni:projectHours ?projectHours .

                OPTIONAL {{ 
                    ?course uni:hasPrerequisite ?prerequisiteCourse .
                    ?prerequisiteCourse uni:courseID ?prerequisiteCourseID ;
                                      uni:courseName ?prerequisiteCourseName .
                }}
                OPTIONAL {{
                    ?programCourseLink uni:partOfOptionalGroup ?optionalGroup .
                    ?optionalGroup uni:optionalGroupID ?optionalGroupID ;
                                 uni:optionalGroupName ?optionalGroupName ;
                                 uni:minCreditsRequired ?minCreditsRequired .
                    OPTIONAL {{ ?optionalGroup uni:optionalGroupDescription ?optionalGroupDescription . }}
                }}
            }}
            ORDER BY ?stipulatedSemester ?requirementType ?courseName
        """
        results_components = get_sparql_results(query_program_components)

        if results_components and results_components["results"]["bindings"]:
            for binding in results_components["results"]["bindings"]:
                course_uri = parse_sparql_binding(binding, "course", "uri")

                # Lưu thông tin course nếu chưa có
                if course_uri not in all_courses_details:
                    all_courses_details[course_uri] = {
                        'uri': course_uri,
                        'id': parse_sparql_binding(binding, "courseID"),
                        'name': parse_sparql_binding(binding, "courseName"),
                        'credits': int(parse_sparql_binding(binding, "credits") or 0),
                        'theory_hours': int(parse_sparql_binding(binding, "theoryHours") or 0),
                        'practice_hours': int(parse_sparql_binding(binding, "practiceHours") or 0),
                        'project_hours': int(parse_sparql_binding(binding, "projectHours") or 0),
                        'prerequisites_uris': set(),  # Dùng set để tránh trùng lặp
                        'prerequisites_display': []
                    }

                # Thêm môn tiên quyết
                prereq_uri = parse_sparql_binding(binding, "prerequisiteCourse", "uri")
                if prereq_uri and prereq_uri not in all_courses_details[course_uri]['prerequisites_uris']:
                    all_courses_details[course_uri]['prerequisites_uris'].add(prereq_uri)
                    # Lưu tên để hiển thị, sẽ cần truy vấn lại hoặc lấy từ binding nếu có
                    prereq_name = parse_sparql_binding(binding, "prerequisiteCourseName")
                    if prereq_name:
                        all_courses_details[course_uri]['prerequisites_display'].append(prereq_name)

                # Phân loại môn học vào học kỳ
                semester = int(parse_sparql_binding(binding, "stipulatedSemester"))
                requirement = parse_sparql_binding(binding,
                                                   "requirementType")  # Ví dụ: "Bắt buộc", "Tự chọn theo nhóm", "Tự chọn đơn lẻ"

                # Tạo một "ctp_like" object để truyền cho template
                ctp_like_object = {
                    'course': all_courses_details[course_uri],  # Đây là dictionary thông tin course
                    'programCourseLinkURI': parse_sparql_binding(binding, "programCourseLink", "uri"),
                    # Các thông tin khác của ProgramCourseLink nếu cần
                }

                optional_group_uri = parse_sparql_binding(binding, "optionalGroup", "uri")
                if requirement and "bắt buộc" in requirement.lower():  # Điều chỉnh logic này cho phù hợp với requirementType của bạn
                    courses_by_semester[semester]['compulsory'].append(ctp_like_object)
                elif optional_group_uri:
                    if optional_group_uri not in optional_groups_details:
                        optional_groups_details[optional_group_uri] = {
                            'uri': optional_group_uri,
                            'id': parse_sparql_binding(binding, "optionalGroupID"),
                            'name': parse_sparql_binding(binding, "optionalGroupName"),
                            'min_credits': int(parse_sparql_binding(binding, "minCreditsRequired") or 0),
                            'description': parse_sparql_binding(binding, "optionalGroupDescription") or ""
                        }
                    # group_id nên là một định danh duy nhất, ví dụ optionalGroupID hoặc URI
                    group_key = optional_groups_details[optional_group_uri]['id']  # Hoặc URI
                    courses_by_semester[semester]['optional_grouped'][group_key].append(ctp_like_object)
                else:  # Tự chọn đơn lẻ
                    courses_by_semester[semester]['optional_individual'].append(ctp_like_object)

            # Tạo chuỗi hiển thị tiên quyết
            for course_detail in all_courses_details.values():
                # Nếu bạn muốn tên môn tiên quyết thay vì chỉ URI, bạn cần đảm bảo đã lấy được tên của chúng.
                # Cách làm hiện tại là lấy từ binding, nếu không có sẽ cần query riêng hoặc đảm bảo query_components có.
                course_detail['prerequisites_str'] = ", ".join(
                    sorted(list(course_detail['prerequisites_display']))) or "Không"

    # Sắp xếp lại dict theo key (học kỳ)
    courses_by_semester = dict(sorted(courses_by_semester.items()))

    # Map lại optional_groups_details từ URI sang ID để template dễ dùng hơn (nếu group_key ở trên dùng URI)
    # Và chuyển optional_grouped trong courses_by_semester sang dùng group_id (nếu đang dùng URI)
    # (Phần này cần tùy chỉnh dựa trên cách bạn chọn group_key ở trên)

    # Ví dụ, nếu optional_groups_details có key là URI, và courses_by_semester[sem]['optional_grouped'] cũng có key là URI:
    temp_optional_groups_by_id = {val['id']: val for val in optional_groups_details.values()}

    for sem_num, sem_content in courses_by_semester.items():
        new_optional_grouped = defaultdict(list)
        for group_uri_key, courses_list in sem_content['optional_grouped'].items():
            # Giả sử group_uri_key là group_id đã lấy từ optional_groups_details[group_uri]['id']
            # Nếu không, bạn cần tìm group_id từ group_uri
            if group_uri_key in temp_optional_groups_by_id:  # Kiểm tra group_id (key của optional_grouped) có trong temp_optional_groups_by_id
                new_optional_grouped[group_uri_key].extend(courses_list)
            # else: # Nếu group_uri_key là URI, tìm id tương ứng
            #   found_group_id = next((gid for gid, gdata in temp_optional_groups_by_id.items() if optional_groups_details.get(group_uri_key, {}).get('id') == gid), None)
            #   if found_group_id:
            #       new_optional_grouped[found_group_id].extend(courses_list)
        sem_content['optional_grouped'] = dict(new_optional_grouped)  # Chuyển về dict thường

    context = {
        'student': student_info,  # Chứa thông tin sinh viên
        'training_program': training_program_details,  # Chứa thông tin chương trình
        'courses_by_semester': courses_by_semester,
        'optional_groups_details': temp_optional_groups_by_id,  # Dùng dict với key là group_id
        'current_user': request.user,
    }
    # Sử dụng cùng template với cách ORM
    return render(request, 'student_portal/student_curriculum.html', context)

# Hiện kết quả học tập
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from trainingprogram.models import Student, Grade  # Giả sử models.py cùng cấp
from collections import defaultdict


@login_required
def student_grades_view(request):
    student_instance = None
    grades_by_semester_year = defaultdict(list)  # { "Năm học 2022-2023 - Học kỳ 1": [grade1, grade2], ... }

    try:
        student_instance = request.user.student
    except Student.DoesNotExist:
        # Xử lý trường hợp người dùng không có hồ sơ sinh viên
        pass  # Template sẽ hiển thị thông báo

    if student_instance:
        # Lấy tất cả điểm của sinh viên, sắp xếp theo năm học và học kỳ
        # Giả định rằng bạn có một cách để sắp xếp theo thứ tự logic của năm học và học kỳ
        # Ví dụ: nếu AcademyYear là chuỗi "2022-2023" và Semester là chuỗi "1", "2", "Hè"
        # Chúng ta có thể cần xử lý sắp xếp phức tạp hơn nếu định dạng không nhất quán

        student_grades = Grade.objects.filter(student=student_instance) \
            .select_related('course') \
            .order_by('AcademyYear', 'Semester')  # Sắp xếp cơ bản

        # Nhóm điểm theo năm học và học kỳ
        for grade in student_grades:
            # Tạo key cho dictionary, ví dụ: "Năm học 2022-2023 - Học kỳ 1"
            # Hoặc "Học kỳ hè - Năm học 2023" tùy theo dữ liệu thực tế của bạn
            # Bạn có thể cần điều chỉnh cách tạo `semester_year_key` này
            if grade.AcademyYear and grade.Semester:
                # Chuyển đổi Semester để sắp xếp đúng (ví dụ, nếu Semester là số)
                try:
                    semester_display = f"Học kỳ {int(grade.Semester)}"
                except ValueError:
                    semester_display = grade.Semester  # Nếu không phải số, giữ nguyên

                semester_year_key = f"Năm học {grade.AcademyYear} - {semester_display}"
            elif grade.AcademyYear:
                semester_year_key = f"Năm học {grade.AcademyYear}"
            elif grade.Semester:
                semester_year_key = f"Học kỳ {grade.Semester}"
            else:
                semester_year_key = "Chưa xác định kỳ học"

            grades_by_semester_year[semester_year_key].append(grade)

    # Để sắp xếp các key của dictionary (tức là các kỳ học) theo thứ tự mong muốn:
    # Cần một hàm sort key phức tạp hơn nếu thứ tự mặc định của chuỗi không đúng
    # Ví dụ, "Năm học 2021-2022 - Học kỳ 2" sẽ đứng trước "Năm học 2021-2022 - Học kỳ Hè" nếu sort chuỗi
    # Đây là một ví dụ đơn giản, bạn có thể cần tinh chỉnh:
    def sort_semester_key(key_str):
        year_part = ""
        semester_part_val = 99  # Mặc định cho những key không chuẩn

        if "Năm học" in key_str:
            year_match = re.search(r'Năm học (\d{4}-\d{4}|\d{4})', key_str)
            if year_match:
                year_part = year_match.group(1)

        if "Học kỳ" in key_str:
            sem_match = re.search(r'Học kỳ (\d+)', key_str)
            if sem_match:
                semester_part_val = int(sem_match.group(1))
            elif "Học kỳ Hè" in key_str or "Học kỳ hè" in key_str:  # Giả sử hè là kỳ 3
                semester_part_val = 3
                # Thêm các trường hợp khác nếu có

        return (year_part, semester_part_val)

    sorted_grades_by_semester_year = dict(
        sorted(grades_by_semester_year.items(), key=lambda item: sort_semester_key(item[0])))

    context = {
        'student': student_instance,
        'grades_by_semester_year': sorted_grades_by_semester_year,
        'current_user': request.user,
    }
    return render(request, 'student_portal/student_grades.html', context)

@login_required()
def curriculum(request):
    student = request.user.student  # Lấy đối tượng Student từ User đang đăng nhập

    # 1. Lấy ngành của sinh viên
    student_major = student.major

    # 2. Lấy năm nhập học của sinh viên (từ model Student)
    # Giả sử trường AcademicYear lưu năm dưới dạng chuỗi hoặc số nguyên
    student_enrollment_year = int(student.AcademicYear)  # Chuyển sang int nếu cần so sánh

    # 3. Tìm chương trình đào tạo phù hợp
    # Lọc các TrainingProgram thuộc về ngành của sinh viên VÀ có StartYear khớp với năm nhập học
    try:
        training_program = TrainingProgram.objects.get(
            major=student_major,
            StartYear=student_enrollment_year
        )
    except TrainingProgram.DoesNotExist:
        training_program = None
    except TrainingProgram.MultipleObjectsReturned:
        # Xử lý trường hợp có nhiều chương trình đào tạo khớp (hiếm khi xảy ra nếu dữ liệu chuẩn)
        # Có thể lấy cái đầu tiên hoặc báo lỗi tùy theo logic bạn muốn
        training_program = TrainingProgram.objects.filter(
            major=student_major,
            StartYear=student_enrollment_year
        ).first()
        # Hoặc:
        # context = {'error_message': "Tìm thấy nhiều chương trình đào tạo phù hợp."}
        # return render(request, 'trainingprogram/training_program.html', context)

    # 4. Lấy danh sách các môn học (CourseTrainingProgram) của chương trình đào tạo đó
    courses_in_program = []
    program_total_credits = 0
    if training_program:
        # Sử dụng related_name 'program_for' từ TrainingProgram đến CourseTrainingProgram
        # hoặc query trực tiếp CourseTrainingProgram
        course_training_program_links = CourseTrainingProgram.objects.filter(
            program=training_program
        ).order_by('semester', 'course__course_name')  # Sắp xếp theo học kỳ, rồi theo tên môn học

        for link in course_training_program_links:
            courses_in_program.append({
                'course_id': link.course.course_id,
                'course_name': link.course.course_name,
                'credits': link.course.credits,
                'semester': link.semester,
                'course_type': link.get_course_type_display(),  # Hiển thị giá trị dễ đọc của course_type
                'prerequisites': ", ".join(
                    [prereq.course_name for prereq in link.course.prerequisites.all()]) or "Không có",
                'optional_group': link.option_G.group_name if link.option_G else None
            })
            program_total_credits += link.course.credits

    context = {
        'student': student,
        'training_program': training_program,
        'danhsachkhoahoc': courses_in_program,
        'program_total_credits': program_total_credits,
    }
    return render(request, 'trainingprogram/training_program.html', context)

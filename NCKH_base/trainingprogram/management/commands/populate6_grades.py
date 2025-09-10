# your_app_name/management/commands/populate_grades.py
'''
python manage.py populate6_grades
'''
import uuid
import csv
import io  # Để đọc string như một file
from django.core.management.base import BaseCommand
from django.db import transaction
# Bỏ validator nếu không cần thiết nữa do đã kiểm tra trong safe_float_cast
# from django.core.validators import MinValueValidator, MaxValueValidator

# Thay 'your_app_name' bằng tên app của bạn
from trainingprogram.models import Grade, Student, Course  # Đảm bảo import đúng

# Hoặc
# from ...models import Grade, Student, Course

RAW_GRADE_DATA_CSV = """STT,MaHocPhan,MaIn,TenHocPhan,ContinuosAssScore,FinalExamScore,Result,Semester,AcademyYear,TestTime
1,PE6021,HP6430,"Bóng rổ-1",7,10,A,,,
2,FL6085,HP4924,"Tiếng Anh Công nghệ thông tin cơ bản-1",,5,C,,,
3,BS6002,HP4828,"Giải tích",,7,B,,,
4,LP6010,HP6817,"Triết học Mác-Lênin",,5,C+,,,
5,BM6091,HP7239,"Quản lý dự án",,7,B+,,,
6,IT6011,HP4771,"Nhập môn về kỹ thuật",,8.5,B+,,,
7,BS6018,HP7201,"Giao tiếp liên văn hóa",,7,C+,,,
8,BS6001,HP4827,"Đại số tuyến tính",,6,C+,,,
9,IT6015,HP4775,"Kỹ thuật lập trình",,7.5,B,,,
10,IT6016,HP4776,"Kỹ thuật số",,7,B,,,
11,LP6011,HP6818,"Kinh tế chính trị Mác-Lênin",,4.5,C,,,
12,BS6024,HP7207,"Mỹ thuật đại cương",,8.5,A,,,
13,FL6086,HP4925,"Tiếng Anh công nghệ thông tin cơ bản-2",,5,C,,,
14,BS6027,HP7210,"Vật lý đại cương",,10,A,,,
15,PE6022,HP6432,"Bóng rổ-2",9,10,A,,,,
16,DC6004,HP7030,"Đường lối QP&AN của ĐCS Việt Nam",9,6,B,,,
17,DC6005,HP7031,"Công tác quốc phòng và an ninh",9,7,B+,,,
18,DC6006,HP7032,"Quân sự chung",9,9,A,,,
19,DC6007,HP7033,"Kỹ thuật chiến đấu bộ binh và chiến thuật",9,9,A,,,
20,LP6012,HP6819,"Chủ nghĩa xã hội khoa học",,5,C,,,
21,IT6126,HP7339,"Hệ thống cơ sở dữ liệu",,8,B+,,,
22,IT6067,HP7166,"Kiến trúc máy tính và hệ điều hành",,5,C,,,
23,FL6087,HP4926,"Tiếng Anh Công nghệ thông tin cơ bản-3",,4,D,,,
24,IT6035,HP4795,"Toán rời rạc",,7,B,,,
25,IT6120,HP7333,"Lập trình hướng đối tượng",,8.5,B+,,,
26,BS6008,HP4834,"Xác suất thống kê",,8,B+,,,
27,IT6002,HP4762,"Cấu trúc dữ liệu và giải thuật",,9.5,A,,,
28,LP6013,HP6820,"Lịch sử Đảng Cộng sản Việt Nam",,5,C,,,
29,IT6001,HP4761,"An toàn và bảo mật thông tin",,9,A,,,
30,IT6083,HP7182,"Mạng máy tính",,9,B+,,,
31,IT6082,HP7181,"Nhập môn công nghệ phần mềm",,8,A,,,
32,IT6066,HP7165,"Phân tích thiết kế phần mềm",,9.5,A,,,
33,PE6017,HP6422,"Bóng bàn-1",8,10,A,,,
34,PE6031,HP6553,"Cầu mây-1",10,10,A,,,
35,LP6004,HP4838,"Tư tưởng Hồ Chí Minh",,6.5,B,,,
36,IT6121,HP7334,"Thực tập cơ sở ngành",,8,B+,,,
37,IT6094,HP7296,"Trí tuệ nhân tạo",,9,B+,,,
38,LP6003,HP4837,"Pháp luật đại cương",,8,B+,,,
39,IT6039,HP4799,"Thiết kế Web",,7.5,B,,,
40,IT6013,HP4773,"Kiểm thử phần mềm",,7.5,B,,,
41,IT6100,HP7313,"Thiết kế đồ hoạ 2D",,8,C+,,,
42,IT6044,HP4804,"Ứng dụng thuật toán",,8,B,,,
43,IT6123,HP7336,"Tương tác người máy",,8,B+,,,
44,FL6088,HP4927,"Tiếng Anh Công nghệ thông tin cơ bản-4",,,,,,,
45,IT6070,HP7169,"An ninh mạng",,,,,,,
46,IT6130,HP7474,"Lập trình Python cơ bản",,,,,,,
47,IT6056,HP6760,"Quản trị mạng trên hệ điều hành Windows",,,,,,,
48,IT6077,HP7176,"Phân tích dữ liệu lớn",,,,,,,
"""
from trainingprogram.management.commands import var_env
# RAW_GRADE_DATA_CSV = var_env.DiemCuaDuong

STUDENT_ID_TO_USE = "f72fc5c2-cba1-448b-ace2-2f953358b45e" # ID cua Minh
# STUDENT_ID_TO_USE = "c949fe71-a71e-4612-958a-8c5173b9b3b7" # ID cua Duong


STUDENT_START_YEAR = 2021  # Năm sinh viên bắt đầu học (ví dụ)
COURSES_PER_SEMESTER_ESTIMATE = 6  # Số môn ước tính mỗi kỳ


class Command(BaseCommand):
    help = 'Populates the Grade table from CSV data for a specific student.'

    def preprocess_csv_grade_data(self, raw_csv_data):
        """
        Tiền xử lý dữ liệu điểm từ chuỗi CSV.
        """
        processed_records = []
        data_io = io.StringIO(raw_csv_data.strip())

        # Bỏ qua dòng header của CSV
        try:
            next(data_io)
        except StopIteration:
            self.stdout.write(self.style.WARNING("CSV data is empty or only has a header."))
            return []

        csv_reader = csv.reader(data_io)

        for row_num, row_parts in enumerate(csv_reader):
            # Kiểm tra xem dòng có đủ phần tử tối thiểu không (ít nhất là STT và Mã HP)
            if not row_parts or len(row_parts) < 2 or not row_parts[0].strip().isdigit():
                if row_parts:  # Nếu không trống mà STT không phải số
                    self.stdout.write(self.style.WARNING(f"Skipping non-data or malformed CSV row: {row_parts[:200]}"))
                continue

            try:
                # Cột trong CSV:
                # 0: STT, 1: MaHocPhan, 2: MaIn, 3: TenHocPhan,
                # 4: ContinuosAssScore, 5: FinalExamScore, 6: Result
                # Các cột sau (Semester, AcademyYear, TestTime) trong CSV đang trống

                record = {
                    "stt": row_parts[0].strip(),
                    "course_id": row_parts[1].strip(),
                    "continuos_score": row_parts[4].strip() if len(row_parts) > 4 else "",
                    "final_score": row_parts[5].strip() if len(row_parts) > 5 else "",
                    "result_char": row_parts[6].strip() if len(row_parts) > 6 and row_parts[6].strip() else None,
                }
                if record["course_id"]:
                    processed_records.append(record)
            except IndexError:
                self.stdout.write(self.style.ERROR(
                    f"Error parsing CSV row {row_num + 1} (IndexError, after header): {row_parts[:200]}"))

        return processed_records

    def safe_float_cast(self, value_str, field_name="Score"):
        """
        Chuyển đổi chuỗi điểm sang float an toàn, kiểm tra None và khoảng giá trị.
        """
        if not value_str or value_str.isspace():
            return None
        try:
            val = float(value_str)
            if not (0.0 <= val <= 10.0):
                self.stdout.write(self.style.WARNING(
                    f"{field_name} '{val}' for input '{value_str}' is out of 0-10 range. Setting to None."))
                return None
            return val
        except ValueError:
            self.stdout.write(
                self.style.WARNING(f"Could not convert '{value_str}' to float for {field_name}. Setting to None."))
            return None

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            student_instance = Student.objects.get(pk=STUDENT_ID_TO_USE)
            student_display_name = getattr(student_instance, 'Fullname', str(student_instance.pk))
            self.stdout.write(f"Populating grades for student: {student_display_name} (ID: {STUDENT_ID_TO_USE})")
        except Student.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"Student with ID '{STUDENT_ID_TO_USE}' not found. Please ensure this student exists."))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching student: {e}"))
            return

        # Cân nhắc việc xóa điểm cũ của sinh viên này (nên cẩn thận)
        # Grade.objects.filter(student=student_instance).delete()
        # self.stdout.write(f"Deleted existing grades for student {student_display_name}.")

        parsed_grades_data = self.preprocess_csv_grade_data(RAW_GRADE_DATA_CSV)
        if not parsed_grades_data:
            self.stdout.write(self.style.WARNING("No grade data was parsed from CSV. Exiting."))
            return

        self.stdout.write(f"Successfully preprocessed {len(parsed_grades_data)} grade entries from CSV.")

        created_count = 0
        updated_count = 0
        skipped_course_count = 0

        for index, grade_entry in enumerate(parsed_grades_data):
            course_id_str = grade_entry['course_id']
            if not course_id_str:
                self.stdout.write(self.style.WARNING(
                    f"Skipping entry at CSV STT {grade_entry.get('stt', 'N/A')} due to missing course_id."))
                skipped_course_count += 1
                continue

            try:
                course_instance = Course.objects.get(course_id=course_id_str)
            except Course.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"Course with ID '{course_id_str}' not found (CSV STT: {grade_entry.get('stt', 'N/A')}). Skipping grade."
                ))
                skipped_course_count += 1
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching course {course_id_str}: {e}"))
                skipped_course_count += 1
                continue

            continuos_score_val = self.safe_float_cast(grade_entry['continuos_score'], "ContinuosAssScore")
            final_score_val = self.safe_float_cast(grade_entry['final_score'], "FinalExamScore")
            result_char_val = grade_entry['result_char']  # Đã xử lý None trong preprocess

            current_course_order = index + 1
            year_offset = (current_course_order - 1) // (COURSES_PER_SEMESTER_ESTIMATE * 2)
            current_academic_year_start_val = STUDENT_START_YEAR + year_offset
            academic_year_str = f"{current_academic_year_start_val}-{current_academic_year_start_val + 1}"

            course_index_in_year = (current_course_order - 1) % (COURSES_PER_SEMESTER_ESTIMATE * 2)
            if course_index_in_year < COURSES_PER_SEMESTER_ESTIMATE:
                semester_str = "1"
            else:
                semester_str = "2"

            test_time_str = "1"  # Vì bạn nói tất cả các lần thi là 1

            grade_obj, created = Grade.objects.update_or_create(
                student=student_instance,
                course=course_instance,
                # Nếu bạn muốn update_or_create dựa trên cả lần thi (nếu có nhiều lần)
                # TestTime=test_time_str,
                defaults={
                    'ContinuosAssScore': continuos_score_val,
                    'FinalExamScore': final_score_val,
                    'Result': result_char_val,
                    'Semester': semester_str,
                    'AcademyYear': academic_year_str,
                    'TestTime': test_time_str,
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            # self.stdout.write(f"{'Created' if created else 'Updated'} grade for {student_display_name} - {course_instance.course_name}")

        self.stdout.write(self.style.SUCCESS(
            f"Finished populating grades. Created: {created_count}, Updated: {updated_count}, Skipped due to course issue: {skipped_course_count}."
        ))
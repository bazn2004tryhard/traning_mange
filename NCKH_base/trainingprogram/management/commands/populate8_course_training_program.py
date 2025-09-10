"""
python manage.py populate8_course_training_program
"""
from django.core.management.base import BaseCommand
from django.db import transaction
# Thay 'your_app_name' bằng tên app của bạn
from trainingprogram.models import CourseTrainingProgram, TrainingProgram, Course, OptionalGroup

# Dữ liệu cấu trúc chương trình đã được trích xuất
PROGRAM_STRUCTURE_DATA = {
    "COMPULSORY": [
        # I.2 Lý luận chính trị (Bắt buộc)
        {"course_id": "LP6010", "semester": 1},
        {"course_id": "LP6011", "semester": 2},
        {"course_id": "LP6012", "semester": 3},
        {"course_id": "LP6013", "semester": 4},
        {"course_id": "LP6004", "semester": 5},
        # I.3 Khoa học xã hội và nhân văn - Kiến thức bắt buộc
        {"course_id": "BS6018", "semester": 1},
        {"course_id": "LP6003", "semester": 6},
        # I.4 Khoa học tự nhiên - Toán học - Tin học - Kiến thức bắt buộc
        {"course_id": "BS6002", "semester": 1},
        {"course_id": "BS6001", "semester": 2},
        {"course_id": "IT6016", "semester": 2},
        {"course_id": "BS6027", "semester": 2},
        {"course_id": "IT6035", "semester": 3},
        # I.6 Giáo dục quốc phòng an ninh (Bắt buộc)
        {"course_id": "DC6005", "semester": 1},
        {"course_id": "DC6004", "semester": 1},
        {"course_id": "DC6007", "semester": 1},
        {"course_id": "DC6006", "semester": 1},
        # II.1 Kiến thức cơ sở - Kiến thức bắt buộc
        {"course_id": "IT6011", "semester": 1},
        {"course_id": "IT6015", "semester": 2},
        {"course_id": "IT6126", "semester": 3},
        {"course_id": "IT6067", "semester": 3},
        {"course_id": "IT6120", "semester": 3},
        {"course_id": "IT6001", "semester": 4},
        {"course_id": "IT6002", "semester": 4},
        {"course_id": "IT6083", "semester": 4},
        {"course_id": "IT6082", "semester": 4},
        {"course_id": "IT6066", "semester": 4},
        {"course_id": "IT6071", "semester": 5},
        {"course_id": "IT6100", "semester": 5},
        {"course_id": "IT6039", "semester": 5},
        {"course_id": "IT6121", "semester": 5},
        {"course_id": "IT6094", "semester": 5},
        {"course_id": "IT6056", "semester": 6},
        # II.2 Kiến thức chuyên ngành - Kiến thức bắt buộc
        {"course_id": "IT6123", "semester": 6},
        {"course_id": "IT6122", "semester": 7},
        {"course_id": "IT6013", "semester": 7},
        {"course_id": "IT6029", "semester": 7},
        {"course_id": "IT6034", "semester": 7},
        # II.3 Thực tập tốt nghiệp và làm đồ án/khóa luận tốt nghiệp (Bắt buộc)
        {"course_id": "IT6129", "semester": 8},
        {"course_id": "IT6128", "semester": 8},
    ],
    "TcNN1": [
        {"course_id": "FL6287", "semester": 1},
        {"course_id": "FL6288", "semester": 2},
        {"course_id": "FL6289", "semester": 3},
        {"course_id": "FL6290", "semester": 4},
    ],
    "TcNN2": [
        {"course_id": "FL6282", "semester": 1},
        {"course_id": "FL6283", "semester": 2},
        {"course_id": "FL6284", "semester": 3},
        {"course_id": "FL6285", "semester": 4},
    ],
    "TcNN3": [
        {"course_id": "FL6292", "semester": 1},
        {"course_id": "FL6293", "semester": 2},
        {"course_id": "FL6294", "semester": 3},
        {"course_id": "FL6295", "semester": 4},
    ],
    "TcNN4": [
        {"course_id": "FL6085", "semester": 1},
        {"course_id": "FL6086", "semester": 2},
        {"course_id": "FL6087", "semester": 3},
        {"course_id": "FL6088", "semester": 4},
    ],
    "TcNNN": [
        {"course_id": "FL6343", "semester": 5},
        {"course_id": "FL6335", "semester": 5},
        {"course_id": "FL6337", "semester": 5},
        {"course_id": "FL6339", "semester": 5},
        {"course_id": "FL6344", "semester": 6},
        {"course_id": "FL6336", "semester": 6},
        {"course_id": "FL6338", "semester": 6},
        {"course_id": "FL6340", "semester": 6},
    ],
    "TcCNTT1": [
        {"course_id": "BS6021", "semester": 1},
        {"course_id": "BS6019", "semester": 1},
        {"course_id": "BS6020", "semester": 1},
        {"course_id": "BM6091", "semester": 1},
    ],
    "TcCNTT2": [
        {"course_id": "BS6022", "semester": 2},
        {"course_id": "BS6024", "semester": 2},
        {"course_id": "BS6023", "semester": 2},
    ],
    "TcCNTT3": [
        {"course_id": "BS6003", "semester": 3},
        {"course_id": "IT6095", "semester": 3},
        {"course_id": "BS6008", "semester": 3},
    ],
    "TcGDTC": [
        {"course_id": "PE6001", "semester": 1}, {"course_id": "PE6005", "semester": 1},
        {"course_id": "PE6017", "semester": 1}, {"course_id": "PE6003", "semester": 1},
        {"course_id": "PE6027", "semester": 1}, {"course_id": "PE6023", "semester": 1},
        {"course_id": "PE6021", "semester": 1}, {"course_id": "PE6025", "semester": 1},
        {"course_id": "PE6031", "semester": 1}, {"course_id": "PE6029", "semester": 1},
        {"course_id": "PE6035", "semester": 1}, {"course_id": "PE6011", "semester": 1},
        {"course_id": "PE6013", "semester": 1}, {"course_id": "PE6015", "semester": 1},
        {"course_id": "PE6019", "semester": 1}, {"course_id": "PE6002", "semester": 2},
        {"course_id": "PE6006", "semester": 2}, {"course_id": "PE6018", "semester": 2},
        {"course_id": "PE6004", "semester": 2}, {"course_id": "PE6028", "semester": 2},
        {"course_id": "PE6024", "semester": 2}, {"course_id": "PE6022", "semester": 2},
        {"course_id": "PE6026", "semester": 2}, {"course_id": "PE6032", "semester": 2},
        {"course_id": "PE6030", "semester": 2}, {"course_id": "PE6036", "semester": 2},
        {"course_id": "PE6012", "semester": 2}, {"course_id": "PE6014", "semester": 2},
        {"course_id": "PE6016", "semester": 2}, {"course_id": "PE6020", "semester": 2},
    ],
    "TcCNTT4": [
        {"course_id": "IT6070", "semester": 6}, {"course_id": "IT6007", "semester": 6},
        {"course_id": "IT6047", "semester": 6}, {"course_id": "IT6057", "semester": 6},
        {"course_id": "IT6125", "semester": 6},
    ],
    "TcCNTT6": [
        {"course_id": "IT6004", "semester": 7}, {"course_id": "IT6085", "semester": 7},
        {"course_id": "IT6061", "semester": 7}, {"course_id": "IT6060", "semester": 7},
        {"course_id": "IT6030", "semester": 7}, {"course_id": "IT6077", "semester": 7},
        {"course_id": "IT6028", "semester": 7}, {"course_id": "IT6127", "semester": 7},
        {"course_id": "IT6044", "semester": 7},
    ],
    "TcCNTT5.1": [
        {"course_id": "IT6017", "semester": 6}, {"course_id": "IT6021", "semester": 7},
    ],
    "TcCNTT5.2": [
        {"course_id": "IT6020", "semester": 6}, {"course_id": "IT6080", "semester": 7},
    ],
    "TcCNTT5.3": [
        {"course_id": "IT6022", "semester": 6}, {"course_id": "IT6124", "semester": 7},
    ],
    "TcCNTT5.4": [
        {"course_id": "IT6130", "semester": 6}, {"course_id": "IT6131", "semester": 7},
    ],
}

# CHỈ ĐỊNH ID CỦA CHƯƠNG TRÌNH ĐÀO TẠO BẠN MUỐN POPULATE
TARGET_PROGRAM_ID = "CNTT_CNTT_K2022"  # <<< THAY THẾ ID NÀY BẰNG ID CTĐT THỰC TẾ CỦA BẠN

# Định nghĩa cho CourseTrainingProgram.course_type
# Giả sử bạn đã định nghĩa C_TYPE trong model CourseTrainingProgram là:
# C_TYPE = ( (0, 'Bắt buộc'), (1, 'Tự chọn'), ... )
# Hoặc nếu không, bạn có thể định nghĩa hằng số ở đây:
COMPULSORY_NATURE = 0
OPTIONAL_NATURE = 1


class Command(BaseCommand):
    help = 'Populates CourseTrainingProgram using pre-structured data, linking to OptionalGroups.'

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            target_program_instance = TrainingProgram.objects.get(program_id=TARGET_PROGRAM_ID)
        except TrainingProgram.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"TrainingProgram with ID '{TARGET_PROGRAM_ID}' does not exist. "
                f"Please create it or update TARGET_PROGRAM_ID in the script."
            ))
            return

        self.stdout.write(
            f"Populating CourseTrainingProgram for Program: {target_program_instance.program_name} ({target_program_instance.program_id})")

        # Tùy chọn: Xóa các bản ghi CTP cũ của chương trình này
        # num_deleted, _ = CourseTrainingProgram.objects.filter(program=target_program_instance).delete()
        # if num_deleted > 0:
        #    self.stdout.write(self.style.WARNING(f"Deleted {num_deleted} existing CourseTrainingProgram entries for program '{TARGET_PROGRAM_ID}'."))

        created_count = 0
        updated_count = 0
        skipped_missing_course = 0
        skipped_missing_group = 0

        for group_key, courses_in_group_list in PROGRAM_STRUCTURE_DATA.items():
            current_option_G_instance = None
            current_course_nature = COMPULSORY_NATURE  # Mặc định là bắt buộc

            if group_key == "COMPULSORY":
                current_course_nature = COMPULSORY_NATURE
                current_option_G_instance = None
            else:  # Đây là một nhóm tự chọn, group_key là tên của OptionalGroup
                current_course_nature = OPTIONAL_NATURE
                try:
                    current_option_G_instance = OptionalGroup.objects.get(group_name=group_key)
                except OptionalGroup.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f"OptionalGroup with name '{group_key}' not found in the database. "
                        f"Skipping all courses intended for this group."
                    ))
                    skipped_missing_group += len(courses_in_group_list)
                    continue  # Bỏ qua tất cả các môn trong nhóm này nếu nhóm không tồn tại

            for course_detail in courses_in_group_list:
                course_id_str = course_detail["course_id"]
                semester_val = course_detail["semester"]  # Đã là integer từ PROGRAM_STRUCTURE_DATA

                try:
                    course_instance = Course.objects.get(course_id=course_id_str)
                except Course.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"Course with ID '{course_id_str}' (intended for group/type '{group_key}') not found. "
                        f"Skipping this CourseTrainingProgram entry."
                    ))
                    skipped_missing_course += 1
                    continue  # Bỏ qua chỉ môn này

                # Tạo hoặc cập nhật bản ghi CourseTrainingProgram
                ctp_entry, created = CourseTrainingProgram.objects.update_or_create(
                    program=target_program_instance,
                    course=course_instance,
                    defaults={
                        'semester': semester_val,
                        'course_type': current_course_nature,  # Sử dụng biến đã xác định
                        'option_G': current_option_G_instance  # Sẽ là None nếu là COMPULSORY
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

                # Log chi tiết nếu muốn (có thể làm chậm nếu nhiều dữ liệu)
                # nature_str = "Bắt buộc" if current_course_nature == COMPULSORY_NATURE else f"Tự chọn (Nhóm: {current_option_G_instance.group_name if current_option_G_instance else 'LỖI NHÓM'})"
                # self.stdout.write(
                #     f"{'Created' if created else 'Updated'} CTP: {target_program_instance.program_id} - {course_instance.course_id} "
                #     f"- HK: {semester_val} - Nature: {nature_str}"
                # )

        self.stdout.write(self.style.SUCCESS(
            f"Finished populating CourseTrainingProgram for '{TARGET_PROGRAM_ID}'.\n"
            f"Total Processed: {created_count + updated_count + skipped_missing_course + skipped_missing_group}\n"
            f"  Created: {created_count}\n"
            f"  Updated: {updated_count}\n"
            f"  Skipped (Course Not Found): {skipped_missing_course}\n"
            f"  Skipped (OptionalGroup Not Found): {skipped_missing_group}"
        ))
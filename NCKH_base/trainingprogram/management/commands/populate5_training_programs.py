# your_app_name/management/commands/populate5_training_programs.py
from django.core.management.base import BaseCommand
from django.db import transaction
# Thay 'your_app_name' bằng tên app của bạn
from trainingprogram.models import TrainingProgram, Major
# Hoặc
# from ...models import TrainingProgram, Major

# Danh sách dữ liệu mẫu cho các Chương trình Đào tạo
# Quan trọng:
# - 'major_id_ref' phải khớp với major_id của các Major đã tồn tại trong database.
# - 'StartYear' là năm bắt đầu của chương trình.
# - 'program_id' nên là duy nhất, có thể kết hợp major_id_ref và StartYear.
SAMPLE_TRAINING_PROGRAMS_DATA = [
    # --- Ngành Công nghệ Thông tin ---
    {
        "program_id": "CNTT_KTPM_K2021",
        "program_name": "Chương trình Kỹ thuật phần mềm Khóa 2021",
        "StartYear": 2021,
        "major_id_ref": "CNTT_KTPM"
    },
    {
        "program_id": "CNTT_KTPM_K2022",
        "program_name": "Chương trình Kỹ thuật phần mềm Khóa 2022",
        "StartYear": 2022,
        "major_id_ref": "CNTT_KTPM"
    },
    {
        "program_id": "CNTT_HTTT_K2021",
        "program_name": "Chương trình Hệ thống thông tin Khóa 2021",
        "StartYear": 2021,
        "major_id_ref": "CNTT_HTTT"
    },
    {
        "program_id": "CNTT_KHMT_K2022",
        "program_name": "Chương trình Khoa học máy tính Khóa 2022",
        "StartYear": 2022,
        "major_id_ref": "CNTT_KHMT"
    },
    # Giả sử bạn có major CNTT_CNTT (Công nghệ thông tin chung)
    {
        "program_id": "CNTT_CNTT_K2023",
        "program_name": "Chương trình Công nghệ thông tin Khóa 2023",
        "StartYear": 2023,
        "major_id_ref": "CNTT_CNTT" # Major này phải tồn tại
    },

    # --- Ngành Kinh tế ---
    {
        "program_id": "KT_QTKD_K2021",
        "program_name": "Chương trình Quản trị kinh doanh Khóa 2021",
        "StartYear": 2021,
        "major_id_ref": "KT_QTKD"
    },
    {
        "program_id": "KT_QTKD_K2022",
        "program_name": "Chương trình Quản trị kinh doanh Khóa 2022",
        "StartYear": 2022,
        "major_id_ref": "KT_QTKD"
    },
    {
        "program_id": "KT_TCNH_K2023",
        "program_name": "Chương trình Tài chính - Ngân hàng Khóa 2023",
        "StartYear": 2023,
        "major_id_ref": "KT_TCNH"
    },

    # --- Ngành Ngoại ngữ ---
    {
        "program_id": "NN_TA_K2022",
        "program_name": "Chương trình Ngôn ngữ Anh Khóa 2022",
        "StartYear": 2022,
        "major_id_ref": "NN_TA"
    },
    {
        "program_id": "NN_TH_K2023",
        "program_name": "Chương trình Ngôn ngữ Hàn Khóa 2023",
        "StartYear": 2023,
        "major_id_ref": "NN_TH"
    },
    # Thêm các chương trình đào tạo khác nếu bạn muốn
]

class Command(BaseCommand):
    help = 'Populates the TrainingProgram table with sample data.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Deleting existing training programs (optional, for clean slate)...")
        # TrainingProgram.objects.all().delete() # Bỏ comment nếu muốn xóa hết dữ liệu cũ

        self.stdout.write("Creating/Updating TrainingProgram objects...")
        for tp_data in SAMPLE_TRAINING_PROGRAMS_DATA:
            major_id_ref = tp_data.get("major_id_ref")
            if not major_id_ref:
                self.stdout.write(self.style.WARNING(
                    f"Skipping training program '{tp_data.get('program_name', 'N/A')}' due to missing 'major_id_ref'."
                ))
                continue

            try:
                # Lấy đối tượng Major dựa trên major_id_ref
                major_instance = Major.objects.get(major_id=major_id_ref)
            except Major.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f"Major with ID '{major_id_ref}' not found for training program '{tp_data.get('program_name', 'N/A')}'. "
                    f"Please ensure major data (with ID: {major_id_ref}) is populated first."
                ))
                continue # Bỏ qua việc tạo training program này nếu không tìm thấy major

            program, created = TrainingProgram.objects.update_or_create(
                program_id=tp_data["program_id"],
                defaults={
                    'program_name': tp_data["program_name"],
                    'StartYear': tp_data["StartYear"],
                    'major': major_instance  # Gán đối tượng Major đã lấy được
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f"Created training program: {program.program_id} - {program.program_name} (Major: {major_instance.major_name})"
                ))
            else:
                self.stdout.write(
                    f"Updated training program: {program.program_id} - {program.program_name} (Major: {major_instance.major_name})"
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated training program data.'))
# your_app_name/management/commands/populate3_majors.py
from django.core.management.base import BaseCommand
from django.db import transaction
# Thay 'your_app_name' bằng tên app của bạn
from trainingprogram.models import Major, Faculty
# Hoặc nếu các model nằm trong file models.py cùng cấp với thư mục management:
# from ...models import Major, Faculty

# Danh sách dữ liệu mẫu cho các Ngành
# Quan trọng: 'faculty_id' phải khớp với faculty_id của các Faculty đã tồn tại trong database
SAMPLE_MAJORS_DATA = [
    {
        "major_id": "CNTT_KTPM",
        "major_name": "Kỹ thuật phần mềm",
        "faculty_id": "CNTT"  # Phải khớp với faculty_id của Khoa Công nghệ Thông tin
    },
    {
        "major_id": "CNTT_HTTT",
        "major_name": "Hệ thống thông tin",
        "faculty_id": "CNTT"
    },
    {
        "major_id": "CNTT_KHMT",
        "major_name": "Khoa học máy tính",
        "faculty_id": "CNTT"
    },
    {
        "major_id": "CNTT_CNTT",
        "major_name": "Công nghệ thông tin",
        "faculty_id": "CNTT"
    },
    {
        "major_id": "KT_QTKD",
        "major_name": "Quản trị kinh doanh",
        "faculty_id": "KT"  # Phải khớp với faculty_id của Khoa Kinh tế
    },
    {
        "major_id": "KT_TCNH",
        "major_name": "Tài chính - Ngân hàng",
        "faculty_id": "KT"
    },
    {
        "major_id": "NN_TA",
        "major_name": "Ngôn ngữ Anh",
        "faculty_id": "NN"  # Phải khớp với faculty_id của Khoa Ngoại ngữ
    },
    {
        "major_id": "NN_TH",
        "major_name": "Ngôn ngữ Hàn",
        "faculty_id": "NN"
    },

    # Thêm các ngành khác nếu bạn muốn
]

class Command(BaseCommand):
    help = 'Populates the Major table with sample data.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Deleting existing majors (optional, for clean slate)...")
        # Major.objects.all().delete() # Bỏ comment nếu muốn xóa hết dữ liệu cũ

        self.stdout.write("Creating/Updating Major objects...")
        for major_data in SAMPLE_MAJORS_DATA:
            faculty_id = major_data.get("faculty_id")
            if not faculty_id:
                self.stdout.write(self.style.WARNING(
                    f"Skipping major '{major_data['major_name']}' due to missing 'faculty_id'."
                ))
                continue

            try:
                # Lấy đối tượng Faculty dựa trên faculty_id
                faculty_instance = Faculty.objects.get(faculty_id=faculty_id)
            except Faculty.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f"Faculty with ID '{faculty_id}' not found for major '{major_data['major_name']}'. "
                    f"Please ensure faculty data is populated first."
                ))
                continue # Bỏ qua việc tạo major này nếu không tìm thấy faculty

            major, created = Major.objects.update_or_create(
                major_id=major_data["major_id"],
                defaults={
                    'major_name': major_data["major_name"],
                    'faculty': faculty_instance  # Gán đối tượng Faculty đã lấy được
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f"Created major: {major.major_id} - {major.major_name} (Faculty: {faculty_instance.faculty_name})"
                ))
            else:
                self.stdout.write(
                    f"Updated major: {major.major_id} - {major.major_name} (Faculty: {faculty_instance.faculty_name})"
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated major data.'))
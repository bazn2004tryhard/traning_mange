# your_app_name/management/commands/populate2_faculties.py
from django.core.management.base import BaseCommand
from django.db import transaction
# Thay 'your_app_name' bằng tên app của bạn nơi chứa model Faculty
from trainingprogram.models import Faculty
# Hoặc nếu model Faculty nằm trong file models.py cùng cấp với thư mục management:
# from ...models import Faculty

# Danh sách dữ liệu mẫu cho các Khoa
SAMPLE_FACULTIES_DATA = [
    {
        "faculty_id": "CNTT",
        "faculty_name": "Công nghệ Thông tin",
        "Phone": "024-3854-xxxx",
        "Email": "cntt@example.edu.vn",
        "Address": "Nhà A1, Đại học Example"
    },
    {
        "faculty_id": "KT",
        "faculty_name": "Kinh tế",
        "Phone": "024-3855-yyyy",
        "Email": "kinhte@example.edu.vn",
        "Address": "Nhà B2, Đại học Example"
    },
    {
        "faculty_id": "NN",
        "faculty_name": "Ngoại ngữ",
        "Phone": "024-3856-zzzz",
        "Email": "ngoaingu@example.edu.vn",
        "Address": "Nhà C3, Đại học Example"
    },
    {
        "faculty_id": "CK",
        "faculty_name": "Cơ khí",
        "Phone": "024-3857-aaaa",
        "Email": "cokhi@example.edu.vn",
        "Address": "Nhà D4, Đại học Example"
    },
    {
        "faculty_id": "XD",
        "faculty_name": "Xây dựng",
        "Phone": "024-3858-bbbb",
        "Email": "xaydung@example.edu.vn",
        "Address": "Nhà E5, Đại học Example"
    },
    # Thêm các khoa khác nếu bạn muốn
]

class Command(BaseCommand):
    help = 'Populates the Faculty table with sample data.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Deleting existing faculties (optional, for clean slate)...")
        # Faculty.objects.all().delete() # Bỏ comment dòng này nếu bạn muốn xóa hết dữ liệu cũ mỗi lần chạy

        self.stdout.write("Creating/Updating Faculty objects...")
        for faculty_data in SAMPLE_FACULTIES_DATA:
            faculty, created = Faculty.objects.update_or_create(
                faculty_id=faculty_data["faculty_id"],
                defaults={
                    'faculty_name': faculty_data["faculty_name"],
                    'Phone': faculty_data.get("Phone"), # Sử dụng .get() để xử lý trường hợp thiếu key
                    'Email': faculty_data.get("Email"),
                    'Address': faculty_data.get("Address", "") # Cung cấp giá trị mặc định nếu thiếu
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created faculty: {faculty.faculty_id} - {faculty.faculty_name}"))
            else:
                self.stdout.write(f"Updated faculty: {faculty.faculty_id} - {faculty.faculty_name}")

        self.stdout.write(self.style.SUCCESS('Successfully populated faculty data.'))
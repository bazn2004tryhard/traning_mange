# your_app_name/management/commands/repopulate_optional_groups.py
# python manage.py populate7_optional_groups
from django.core.management.base import BaseCommand
from django.db import transaction
import uuid  # Mặc dù không set ID, import vẫn có thể cần nếu model dùng
# Thay 'your_app_name' bằng tên app của bạn
from trainingprogram.models import OptionalGroup

# Dữ liệu bạn cung cấp, được chuyển thành một cấu trúc dễ xử lý
# Mỗi tuple chứa: (group_name, course_type, min_credits, description_base)
# Description sẽ được tạo tự động dựa trên description_base và group_name
CORRECTED_OPTIONAL_GROUP_DATA = [
    ("TcNN4", 99, 20, "Nhóm tự chọn"),
    ("TcCNTT1", 99, 2, "Nhóm tự chọn"),
    ("TcNN2", 99, 20, "Nhóm tự chọn"),
    ("TcNN3", 99, 20, "Nhóm tự chọn"),
    ("TcNN1", 99, 20, "Nhóm tự chọn"),
    ("TcNNN", 99, 10, "Nhóm tự chọn"),  # Sửa min_credits cho TcNNN từ 0 thành 10 như dữ liệu CTĐT
    ("TcCNTT5.3", 99, 6, "Nhóm tự chọn"),
    ("TcCNTT5.4", 99, 6, "Nhóm tự chọn"),
    ("TcGDTC", 99, 4, "Nhóm tự chọn"),
    ("TcCNTT3", 99, 3, "Nhóm tự chọn"),
    ("TcCNTT5.1", 99, 6, "Nhóm tự chọn"),
    ("TcCNTT4", 99, 3, "Nhóm tự chọn"),
    ("TcCNTT6", 99, 6, "Nhóm tự chọn"),
    ("TcCNTT2", 99, 2, "Nhóm tự chọn"),
    ("TcCNTT5.2", 99, 6, "Nhóm tự chọn"),
    # Thêm nhóm "Tc Ôn tập NN" nếu bạn muốn nó có trong OptionalGroup
    # Ví dụ: ("Tc Ôn tập NN", 99, 0, "Nhóm tự chọn Ôn tập Ngoại ngữ"),
]


class Command(BaseCommand):
    help = 'Re-populates or updates the OptionalGroup table with corrected data.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Repopulating/Updating OptionalGroup data with corrected values...")

        # Nếu bạn muốn xóa sạch trước khi tạo lại (CẨN THẬN VỚI DỮ LIỆU LIÊN QUAN)
        # OptionalGroup.objects.all().delete()
        # self.stdout.write(self.style.WARNING("DELETED all existing OptionalGroups."))

        created_count = 0
        updated_count = 0

        for group_name_val, course_type_val, min_credits_val, desc_base in CORRECTED_OPTIONAL_GROUP_DATA:

            description_val = f"{desc_base} {group_name_val}"

            optional_group, created = OptionalGroup.objects.update_or_create(
                group_name=group_name_val,
                defaults={
                    'course_type': course_type_val,
                    'min_credits': min_credits_val,
                    'description': description_val,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Created OptionalGroup: {optional_group.group_name} "
                    f"(Type: {optional_group.course_type}, MinCredits: {optional_group.min_credits}, Desc: '{optional_group.description}')"
                ))
            else:
                updated_count += 1
                self.stdout.write(
                    f"Updated OptionalGroup: {optional_group.group_name} "
                    f"(Type: {optional_group.course_type}, MinCredits: {optional_group.min_credits}, Desc: '{optional_group.description}')"
                )

        self.stdout.write(self.style.SUCCESS(
            f"Finished repopulating/updating OptionalGroups. Created: {created_count}, Updated: {updated_count}."
        ))
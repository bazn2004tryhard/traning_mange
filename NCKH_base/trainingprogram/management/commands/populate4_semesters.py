# your_app_name/management/commands/populate4_semesters.py
import datetime
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.db import transaction
# Thay 'your_app_name' bằng tên app của bạn
from trainingprogram.models import Semester


# Hoặc
# from ...models import Semester

class Command(BaseCommand):
    help = 'Populates the Semester table with data from 2021 to 2027.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Deleting existing semesters (optional, for clean slate)...")
        # Semester.objects.all().delete() # Bỏ comment nếu muốn xóa hết dữ liệu cũ

        self.stdout.write("Generating and populating Semester data...")

        start_year = 2021
        end_year = 2027

        semesters_to_create = []

        for year in range(start_year, end_year + 1):
            # --- Năm học YYYY - (YYYY+1) ---

            # Kỳ 1 Chính (Thường bắt đầu tháng 9)
            # Ví dụ: 20211_MAIN: Học kỳ 1 năm học 2021-2022
            sem1_main_start = datetime.date(year, 9, 1)
            sem1_main_end = datetime.date(year, 12, 31)
            semesters_to_create.append(
                Semester(
                    ID=f"{year}1_MAIN",
                    SemesterName=f"Học kỳ 1 năm học {year}-{year + 1} (Chính)",
                    StartDate=sem1_main_start,
                    EndDate=sem1_main_end
                )
            )

            # Kỳ 1 Phụ (Sau kỳ 1 chính, kéo dài 1.5 tháng)
            # Ví dụ: 20211_SUB: Học kỳ 1 Phụ năm học 2021-2022
            sem1_sub_start = sem1_main_end + relativedelta(days=1)  # Bắt đầu ngay sau kỳ chính
            sem1_sub_end = sem1_sub_start + relativedelta(months=1, days=15)  # 1.5 tháng
            semesters_to_create.append(
                Semester(
                    ID=f"{year}1_SUB",
                    SemesterName=f"Học kỳ 1 Phụ năm học {year}-{year + 1}",
                    StartDate=sem1_sub_start,
                    EndDate=sem1_sub_end
                )
            )

            # Kỳ 2 Chính (Thường bắt đầu tháng 2 năm sau)
            # Ví dụ: 20212_MAIN: Học kỳ 2 năm học 2021-2022
            sem2_main_start_year = year + 1
            sem2_main_start = datetime.date(sem2_main_start_year, 2, 15)  # Giả định bắt đầu giữa tháng 2
            sem2_main_end = datetime.date(sem2_main_start_year, 6, 30)  # Kết thúc cuối tháng 6
            semesters_to_create.append(
                Semester(
                    ID=f"{year}2_MAIN",  # Vẫn dùng year của năm bắt đầu năm học cho ID
                    SemesterName=f"Học kỳ 2 năm học {year}-{year + 1} (Chính)",
                    StartDate=sem2_main_start,
                    EndDate=sem2_main_end
                )
            )

            # Kỳ 2 Phụ (Hè - Sau kỳ 2 chính, kéo dài 1.5 tháng)
            # Ví dụ: 20212_SUB: Học kỳ Hè năm học 2021-2022
            sem2_sub_start = sem2_main_end + relativedelta(days=1)  # Bắt đầu ngay sau kỳ chính
            sem2_sub_end = sem2_sub_start + relativedelta(months=1, days=15)  # 1.5 tháng
            semesters_to_create.append(
                Semester(
                    ID=f"{year}2_SUB",  # Vẫn dùng year của năm bắt đầu năm học cho ID
                    SemesterName=f"Học kỳ Hè năm học {year}-{year + 1} (Phụ)",
                    StartDate=sem2_sub_start,
                    EndDate=sem2_sub_end
                )
            )

        # Sử dụng bulk_create để hiệu quả hơn khi tạo nhiều đối tượng
        try:
            Semester.objects.bulk_create(semesters_to_create, ignore_conflicts=True)
            # ignore_conflicts=True: nếu ID đã tồn tại thì bỏ qua, không gây lỗi
            # Nếu bạn muốn update_or_create từng cái thì dùng vòng lặp như các script trước

            # Hoặc nếu muốn update_or_create:
            # for sem_data in semesters_to_create:
            #     obj, created = Semester.objects.update_or_create(
            #         ID=sem_data.ID,
            #         defaults={
            #             'SemesterName': sem_data.SemesterName,
            #             'StartDate': sem_data.StartDate,
            #             'EndDate': sem_data.EndDate,
            #         }
            #     )
            #     if created:
            #         self.stdout.write(self.style.SUCCESS(f"Created semester: {obj.ID} - {obj.SemesterName}"))
            #     else:
            #         self.stdout.write(f"Updated semester: {obj.ID} - {obj.SemesterName}")

            self.stdout.write(self.style.SUCCESS(
                f"Successfully populated/updated semester data for {len(semesters_to_create)} semesters."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
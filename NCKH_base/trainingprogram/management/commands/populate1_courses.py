
import re
from django.core.management.base import BaseCommand
from django.db import transaction
# Thay 'my_app' bằng tên app của bạn nơi chứa model Course
# from my_app.models import Course
# Hoặc nếu model Course nằm trong file models.py cùng cấp với thư mục management:
from ...models import Course  # Giả sử Course model nằm trong my_app/models.py

# Dán toàn bộ danh sách môn học bạn cung cấp vào đây
RAW_COURSE_DATA = """
STT
Mã học phần	Tên học phần	Số tín chỉ	Loại giờ tín chỉ	Học kỳ	Kiểu học phần	Học phần (theo mã)
LT	TH	Lý thuyết	BTL/ĐA	Thảo luận	Thực hành thí nghiệm, điền dã, studio	Hướng dẫn sinh viên tự học	Tiên quyết	Học trước
I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG
I.1	Ngoài khung	20.00							Có tự chọn				
Kiến thức bắt buộc	-60.00	-60.00	0.00	0.00								
TcNN1	20	20	0	0					
1	FL6287	Tiếng Hàn cơ bản-1	5.0	2.67	0.00	0	0	0	0	0	1			
2	FL6288	Tiếng Hàn cơ bản-2	5.0	2.67	0.00	0	0	0	0	0	2			FL6287
3	FL6289	Tiếng Hàn cơ bản-3	5.0	2.67	0.00	0	0	0	0	0	3			FL6288
4	FL6290	Tiếng Hàn cơ bản-4	5.0	2.67	0.00	0	0	0	0	0	4			FL6289
TcNN2	20	20	0	0					
1	FL6282	Tiếng Trung cơ bản-1	5.0	2.67	0.00	0	0	0	0	0	1			
2	FL6283	Tiếng Trung cơ bản-2	5.0	2.67	0.00	0	0	0	0	0	2			FL6282
3	FL6284	Tiếng Trung cơ bản-3	5.0	2.67	0.00	0	0	0	0	0	3		FL6283	FL6282,FL6283
4	FL6285	Tiếng Trung cơ bản-4	5.0	2.67	0.00	0	0	0	0	0	4		FL6283	FL6284
TcNN3	20	20	0	0					
1	FL6292	Tiếng Nhật cơ bản-1	5.0	2.67	0.00	0	0	0	0	0	1			
2	FL6293	Tiếng Nhật cơ bản-2	5.0	2.67	0.00	0	0	0	0	0	2			FL6292
3	FL6294	Tiếng Nhật cơ bản-3	5.0	2.67	0.00	0	0	0	0	0	3			FL6293
4	FL6295	Tiếng Nhật cơ bản-4	5.0	2.67	0.00	0	0	0	0	0	4		FL6293	FL6294
TcNN4	20	20	0	0					
1	FL6085	Tiếng Anh Công nghệ thông tin cơ bản-1	5.0	2.67	0.00	0	0	0	0	0	1			
2	FL6086	Tiếng Anh công nghệ thông tin cơ bản-2	5.0	2.67	0.00	0	0	0	0	0	2			FL6085
3	FL6087	Tiếng Anh Công nghệ thông tin cơ bản-3	5.0	2.67	0.00	0	0	0	0	0	3		FL6085	FL6086
4	FL6088	Tiếng Anh Công nghệ thông tin cơ bản-4	5.0	2.67	0.00	0	0	0	0	0	4		FL6086	FL6087
Tc Ôn tập NN	0	0	0	0					
1	FL6085OT	Ôn tập Tiếng Anh Công nghệ thông tin cơ bản-1	3.0	1.00	0.00	0	0	0	0	0	1			
2	FL6086OT	Ôn tập Tiếng Anh công nghệ thông tin cơ bản-2	3.0	1.00	0.00	0	0	0	0	0	1			
3	FL6087OT	Ôn tập Tiếng Anh Công nghệ thông tin cơ bản-3	3.0	1.00	0.00	0	0	0	0	0	1			
4	FL6088OT	Ôn tập Tiếng Anh Công nghệ thông tin cơ bản-4	3.0	1.00	0.00	0	0	0	0	0	1			
5	FL6287OT	Ôn tập Tiếng Hàn cơ bản-1	3.0	1.00	0.00	0	0	0	0	0	1			
6	FL6288OT	Ôn tập Tiếng Hàn cơ bản-2	3.0	1.00	0.00	0	0	0	0	0	1			
7	FL6289OT	Ôn tập Tiếng Hàn cơ bản-3	3.0	1.00	0.00	0	0	0	0	0	1			
8	FL6290OT	Ôn tập Tiếng Hàn cơ bản-4	3.0	1.00	0.00	0	0	0	0	0	1			
9	FL6292OT	Ôn tập Tiếng Nhật cơ bản-1	3.0	1.00	0.00	0	0	0	0	0	1			
10	FL6293OT	Ôn tập Tiếng Nhật cơ bản-2	3.0	1.00	0.00	0	0	0	0	0	1			
11	FL6294OT	Ôn tập Tiếng Nhật cơ bản-3	3.0	1.00	0.00	0	0	0	0	0	1			
12	FL6295OT	Ôn tập Tiếng Nhật cơ bản-4	3.0	1.00	0.00	0	0	0	0	0	1			
13	FL6282OT	Ôn tập Tiếng Trung cơ bản-1	3.0	1.00	0.00	0	0	0	0	0	1			
14	FL6283OT	Ôn tập Tiếng Trung cơ bản-2	3.0	1.00	0.00	0	0	0	0	0	1			
15	FL6284OT	Ôn tập Tiếng Trung cơ bản-3	3.0	1.00	0.00	0	0	0	0	0	1			
16	FL6285OT	Ôn tập Tiếng Trung cơ bản-4	3.0	1.00	0.00	0	0	0	0	0	1			
I.2	Lý luận chính trị	11.00							Bắt buộc				
1	LP6010	Triết học Mác-Lênin	3.0	3.00	0.00	0	0	0	0	0	1			
2	LP6011	Kinh tế chính trị Mác-Lênin	2.0	2.00	0.00	0	0	0	0	0	2			
3	LP6012	Chủ nghĩa xã hội khoa học	2.0	2.00	0.00	0	0	0	0	0	3			LP6010
4	LP6013	Lịch sử Đảng Cộng sản Việt Nam	2.0	2.00	0.00	0	0	0	0	0	4			
5	LP6004	Tư tưởng Hồ Chí Minh	2.0	2.00	0.00	0	0	0	0	0	5			LP6010,LP6012
I.3	Khoa học xã hội và nhân văn	18.00							Có tự chọn				
Kiến thức bắt buộc	4.00	4.00	0.00	0.00								
1	BS6018	Giao tiếp liên văn hóa	2.0	2.00	0.00	0	0	0	0	0	1			
2	LP6003	Pháp luật đại cương	2.0	2.00	0.00	0	0	0	0	0	6			LP6004,LP6013
TcNNN	10	10	0	0					
1	FL6343	Tiếng Anh Công nghệ thông tin-1	5.0	5.00	0.00	0	0	0	0	0	5		FL6087	FL6088
2	FL6335	Tiếng Hàn-1	5.0	5.00	0.00	0	0	0	0	0	5			FL6290
3	FL6337	Tiếng Nhật-1	5.0	5.00	0.00	0	0	0	0	0	5			FL6295
4	FL6339	Tiếng Trung-1	5.0	5.00	0.00	0	0	0	0	0	5		FL6284	FL6284,FL6285
5	FL6344	Tiếng Anh Công nghệ thông tin-2	5.0	5.00	0.00	0	0	0	0	0	6		FL6088	FL6343
6	FL6336	Tiếng Hàn-2	5.0	5.00	0.00	0	0	0	0	0	6			FL6335
7	FL6338	Tiếng Nhật-2	5.0	5.00	0.00	0	0	0	0	0	6			FL6337
8	FL6340	Tiếng Trung-2	5.0	5.00	0.00	0	0	0	0	0	6		FL6285	FL6339
TcCNTT1	2	2	0	0					
1	BS6021	Con người và môi trường	2.0	2.00	0.00	0	0	0	0	0	1			
2	BS6019	Nhập môn nghiên cứu khoa học	2.0	2.00	0.00	0	0	0	0	0	1			
3	BS6020	Quan hệ lao động và việc làm	2.0	2.00	0.00	0	0	0	0	0	1			
4	BM6091	Quản lý dự án	2.0	2.00	0.00	0	0	0	0	0	1			
TcCNTT2	2	2	0	0					
1	BS6022	Âm nhạc đại cương	2.0	2.00	0.00	0	0	0	0	0	2			
2	BS6024	Mỹ thuật đại cương	2.0	2.00	0.00	0	0	0	0	0	2			LP6011
3	BS6023	Nghệ thuật học đại cương	2.0	2.00	0.00	0	0	0	0	0	2			
I.4	Khoa học tự nhiên - Toán học - Tin học	18.00							Có tự chọn				
Kiến thức bắt buộc	15.00	15.00	0.00	0.00								
1	BS6002	Giải tích	3.0	3.00	0.00	0	0	0	0	0	1			
2	BS6001	Đại số tuyến tính	3.0	3.00	0.00	0	0	0	0	0	2			
3	IT6016	Kỹ thuật số	3.0	3.00	0.00	0	0	0	0	0	2			
4	BS6027	Vật lý đại cương	3.0	2.00	1.00	0	0	0	0	0	2			
5	IT6035	Toán rời rạc	3.0	3.00	0.00	0	0	0	0	0	3		BS6001	BS6001
TcCNTT3	3	3	0	0					
1	BS6003	Phương pháp tính	3.0	3.00	0.00	0	0	0	0	0	3			BS6002
2	IT6095	Tối ưu hóa	3.0	2.00	1.00	0	0	0	0	0	3			
3	BS6008	Xác suất thống kê	3.0	3.00	0.00	0	0	0	0	0	3			BS6002
I.5	Giáo dục thể chất	4.00							Có tự chọn				
Kiến thức bắt buộc	4.00	4.00	0.00	0.00								
TcGDTC	0	0	0	0					
1	PE6001	Aerobic-1	1.0	0.00	1.00	0	0	0	0	0	1			
2	PE6005	Bơi-1	1.0	0.00	1.00	0	0	0	0	0	1			
3	PE6017	Bóng bàn-1	1.0	0.00	1.00	0	0	0	0	0	1			
4	PE6003	Bóng chuyền-1	1.0	0.00	1.00	0	0	0	0	0	1			
5	PE6027	Bóng đá-1	1.0	0.00	1.00	0	0	0	0	0	1			
6	PE6023	Bóng ném-1	1.0	0.00	1.00	0	0	0	0	0	1			
7	PE6021	Bóng rổ-1	1.0	0.00	1.00	0	0	0	0	0	1			
8	PE6025	Cầu lông-1	1.0	0.00	1.00	0	0	0	0	0	1			
9	PE6031	Cầu mây-1	1.0	0.00	1.00	0	0	0	0	0	1			
10	PE6029	Đá cầu-1	1.0	0.00	1.00	0	0	0	0	0	1			
11	PE6035	Futsal-1	1.0	0.00	1.00	0	0	0	0	0	1			
12	PE6011	Karate-1	1.0	0.00	1.00	0	0	0	0	0	1			
13	PE6013	Khiêu vũ-1	1.0	0.00	1.00	0	0	0	0	0	1			
14	PE6015	Pencak Silat-1	1.0	0.00	1.00	0	0	0	0	0	1			
15	PE6019	Tennis-1	1.0	0.00	1.00	0	0	0	0	0	1			
16	PE6002	Aerobic-2	1.0	0.00	1.00	0	0	0	0	0	2			
17	PE6006	Bơi-2	1.0	0.00	1.00	0	0	0	0	0	2			
18	PE6018	Bóng bàn-2	1.0	0.00	1.00	0	0	0	0	0	2			
19	PE6004	Bóng chuyền-2	1.0	0.00	1.00	0	0	0	0	0	2			
20	PE6028	Bóng đá-2	1.0	0.00	1.00	0	0	0	0	0	2			
21	PE6024	Bóng ném-2	1.0	0.00	1.00	0	0	0	0	0	2			
22	PE6022	Bóng rổ-2	1.0	0.00	1.00	0	0	0	0	0	2			
23	PE6026	Cầu lông-2	1.0	0.00	1.00	0	0	0	0	0	2			
24	PE6032	Cầu mây-2	1.0	0.00	1.00	0	0	0	0	0	2			
25	PE6030	Đá cầu-2	1.0	0.00	1.00	0	0	0	0	0	2			
26	PE6036	Futsal-2	1.0	0.00	1.00	0	0	0	0	0	2			
27	PE6012	Karate-2	1.0	0.00	1.00	0	0	0	0	0	2			
28	PE6014	Khiêu vũ-2	1.0	0.00	1.00	0	0	0	0	0	2			
29	PE6016	Pencak Silat-2	1.0	0.00	1.00	0	0	0	0	0	2			
30	PE6020	Tennis-2	1.0	0.00	1.00	0	0	0	0	0	2			
I.6	Giáo dục quốc phòng an ninh	8.50							Bắt buộc				
1	DC6005	Công tác quốc phòng và an ninh	2.0	2.00	0.00	22	0	8	0	0	1			
2	DC6004	Đường lối QP&AN của ĐCS Việt Nam	3.0	3.00	0.00	37	0	8	0	0	1			
3	DC6007	Kỹ thuật chiến đấu bộ binh và chiến thuật	2.0	0.00	2.00	4	0	0	56	0	1			
4	DC6006	Quân sự chung	1.5	1.00	0.50	14	0	0	16	0	1			
II. KIẾN THỨC GIÁO DỤC CHUYÊN NGHIỆP
II. KIẾN THỨC GIÁO DỤC CHUYÊN NGHIỆP
II.1	Kiến thức cơ sở	51.00							Có tự chọn				
Kiến thức bắt buộc	48.00	48.00	0.00	0.00								
1	IT6011	Nhập môn về kỹ thuật	2.0	2.00	0.00	0	0	0	0	0	1			
2	IT6015	Kỹ thuật lập trình	3.0	2.00	1.00	0	0	0	0	0	2			
3	IT6126	Hệ thống cơ sở dữ liệu	4.0	3.00	1.00	0	0	0	0	0	3			
4	IT6067	Kiến trúc máy tính và hệ điều hành	3.0	3.00	0.00	0	0	0	0	0	3			
5	IT6120	Lập trình hướng đối tượng	3.0	2.00	1.00	0	0	0	0	0	3			IT6015
6	IT6001	An toàn và bảo mật thông tin	3.0	2.50	0.50	0	0	0	0	0	4			IT6015
7	IT6002	Cấu trúc dữ liệu và giải thuật	3.0	2.00	1.00	0	0	0	0	0	4		IT6015	IT6015
8	IT6083	Mạng máy tính	3.0	2.00	1.00	0	0	0	0	0	4			IT6067
9	IT6082	Nhập môn công nghệ phần mềm	3.0	2.00	1.00	0	0	0	0	0	4			IT6015
10	IT6066	Phân tích thiết kế phần mềm	3.0	2.00	1.00	0	0	0	0	0	4		IT6126	IT6126
11	IT6071	Phát triển dự án công nghệ thông tin	3.0	2.00	1.00	0	0	0	0	0	5			
12	IT6100	Thiết kế đồ hoạ 2D	3.0	2.00	1.00	0	0	0	0	0	5			
13	IT6039	Thiết kế Web	3.0	3.00	0.00	0	0	0	0	0	5			IT6015
14	IT6121	Thực tập cơ sở ngành	3.0	0.00	3.00	0	0	0	0	0	5			
15	IT6094	Trí tuệ nhân tạo	3.0	2.00	1.00	0	0	0	0	0	5			
16	IT6056	Quản trị mạng trên hệ điều hành Windows	3.0	2.00	1.00	0	0	0	0	0	6			IT6083_TA
TcCNTT4	3	3	0	0					
1	IT6070	An ninh mạng	3.0	2.00	1.00	0	0	0	0	0	6			IT6083
2	IT6007	Cơ sở lập trình nhúng	3.0	2.00	1.00	0	0	0	0	0	6			IT6015,IT6016,IT6067
3	IT6047	Học máy	3.0	3.00	0.00	0	0	0	0	0	6		IT6043,IT6094	IT6094
4	IT6057	Phát triển ứng dụng thương mại điện tử	3.0	2.00	1.00	0	0	0	0	0	6			IT6015,IT6126
5	IT6125	Thiết kế web nâng cao	3.0	2.00	1.00	0	0	0	0	0	6		IT6039,IT6039_TA	
II.2	Kiến thức chuyên ngành	27.00							Có tự chọn				
Kiến thức bắt buộc	15.00	15.00	0.00	0.00								
1	IT6123	Tương tác người máy	3.0	2.00	1.00	0	0	0	0	0	6			
2	IT6122	Đồ án chuyên ngành	3.0	0.00	3.00	0	0	0	0	0	7			
3	IT6013	Kiểm thử phần mềm	3.0	2.50	0.50	0	0	0	0	0	7			IT6026,IT6066
4	IT6029	Phát triển ứng dụng trên thiết bị di động	3.0	2.00	1.00	0	0	0	0	0	7			IT6015,IT6016,IT6120
5	IT6034	Tích hợp hệ thống phần mềm	3.0	2.00	1.00	0	0	0	0	0	7			
TcCNTT6	6	6	0	0					
1	IT6004	Công nghệ đa phương tiện	3.0	2.00	1.00	0	0	0	0	0	7			
2	IT6085	Đảm bảo chất lượng phần mềm	3.0	2.00	1.00	0	0	0	0	0	7			
3	IT6061	Hệ quản trị doanh nghiệp điện tử	3.0	2.00	1.00	0	0	0	0	0	7			
4	IT6060	Lập trình hệ thống nhúng và Internet vạn vật	3.0	2.00	1.00	0	0	0	0	0	7			IT6015
5	IT6030	Phần mềm mã nguồn mở	3.0	2.00	1.00	0	0	0	0	0	7			IT6082
6	IT6077	Phân tích dữ liệu lớn	3.0	2.00	1.00	0	0	0	0	0	7			
7	IT6028	Phát triển ứng dụng Game	3.0	2.00	1.00	0	0	0	0	0	7			IT6017,IT6018
8	IT6127	Quản trị mạng trên hệ điều hành mã nguồn mở	3.0	2.00	1.00	0	0	0	0	0	7			
9	IT6044	Ứng dụng thuật toán	3.0	2.00	1.00	0	0	0	0	0	7			IT6015
TcCNTT5.1	6	6	0	0					
1	IT6017	Lập trình .NET	3.0	2.00	1.00	0	0	0	0	0	6			IT6120
2	IT6021	Lập trình Web bằng ASP.NET	3.0	2.00	1.00	0	0	0	0	0	7			IT6017
TcCNTT5.2	6	6	0	0					
1	IT6020	Lập trình Java nâng cao	3.0	2.00	1.00	0	0	0	0	0	6		IT6019	IT6019
2	IT6080	Lập trình Web bằng Java	3.0	2.00	1.00	0	0	0	0	0	7			IT6019,IT6020
TcCNTT5.3	6	6	0	0					
1	IT6022	Lập trình web bằng PHP	3.0	2.00	1.00	0	0	0	0	0	6			
2	IT6124	Lập trình PHP nâng cao	3.0	2.00	1.00	0	0	0	0	0	7			IT6022
TcCNTT5.4	6	6	0	0					
1	IT6130	Lập trình Python cơ bản	3.0	2.00	1.00	0	0	0	0	0	6			
2	IT6131	Lập trình Python nâng cao	3.0	2.00	1.00	0	0	0	0	0	7		IT6130	IT6130
II.3	Thực tập tốt nghiệp và làm đồ án/khóa luận tốt nghiệp	15.00							Bắt buộc				
1	IT6129	Đồ án tốt nghiệp	9.0	0.00	9.00	0	0	0	0	0	8			
2	IT6128	Thực tập doanh nghiệp	6.0	0.00	6.00	0	0	0	0	0	8			
"""


class Command(BaseCommand):
    help = 'Populates the Course table from predefined data.'

    def safe_int_cast(self, value_str, default=0):
        try:
            return int(float(value_str))
        except ValueError:
            return default

    def parse_prerequisites(self, prereq_tien_quyet_str, prereq_hoc_truoc_str):
        codes = []
        # Ưu tiên Tiên quyết
        if prereq_tien_quyet_str and prereq_tien_quyet_str.strip():
            raw_codes = prereq_tien_quyet_str.strip().replace(" ", "").split(',')
        elif prereq_hoc_truoc_str and prereq_hoc_truoc_str.strip():
            raw_codes = prereq_hoc_truoc_str.strip().replace(" ", "").split(',')
        else:
            return []

        for code in raw_codes:
            if code:  # Đảm bảo code không rỗng
                codes.append(code)
        return codes

    def handle(self, *args, **options):
        lines = RAW_COURSE_DATA.strip().split('\n')

        # Regex để trích xuất dữ liệu từ các dòng hợp lệ
        # STT | Mã HP | Tên HP | Số TC | LT_factor | TH_factor | LT_hours | BTL/DA_hours | ThaoLuan_hours | TH_TN_hours | HDTH_hours | HocKy | TienQuyet | HocTruoc
        # Nhóm 1: STT (bỏ qua)
        # Nhóm 2: Mã học phần (course_id)
        # Nhóm 3: Tên học phần (course_name)
        # Nhóm 4: Số tín chỉ (credits)
        # Nhóm 5: LT factor (bỏ qua)
        # Nhóm 6: TH factor (bỏ qua)
        # Nhóm 7: Lý thuyết (theory_hours)
        # Nhóm 8: BTL/ĐA (project_hours)
        # Nhóm 9: Thảo luận (bỏ qua)
        # Nhóm 10: Thực hành TN... (practice_hours)
        # Nhóm 11: HD tự học (bỏ qua)
        # Nhóm 12: Học kỳ (bỏ qua)
        # Nhóm 13: Tiên quyết
        # Nhóm 14: Học trước
        course_pattern = re.compile(
            r"^\d+\s+"  # STT (bỏ qua)
            r"([A-Z0-9_OT]+)\s+"  # Mã học phần (course_id) - Group 1
            r"(.+?)\s+"  # Tên học phần (course_name) - Group 2
            r"([\d.]+)\s+"  # Số tín chỉ (credits) - Group 3
            r"([\d.]+)\s+"  # LT factor (bỏ qua) - Group 4
            r"([\d.]+)\s+"  # TH factor (bỏ qua) - Group 5
            r"([\d.]+)\s+"  # Lý thuyết (theory_hours) - Group 6
            r"([\d.]+)\s+"  # BTL/ĐA (project_hours) - Group 7
            r"([\d.]+)\s+"  # Thảo luận (bỏ qua) - Group 8
            r"([\d.]+)\s+"  # Thực hành TN... (practice_hours) - Group 9
            r"([\d.]+)\s+"  # HD tự học (bỏ qua) - Group 10
            r"([\d.]+)\s*"  # Học kỳ (bỏ qua) - Group 11
            r"([A-Z0-9,_ ]*?)\s*"  # Tiên quyết - Group 12 (cho phép rỗng, dấu phẩy, chữ, số, cách)
            r"([A-Z0-9,_ ]*?)\s*$"  # Học trước - Group 13 (cho phép rỗng, dấu phẩy, chữ, số, cách)
        )

        parsed_courses_data = []

        self.stdout.write("Parsing course data...")
        for line in lines:
            line = line.strip()
            match = course_pattern.match(line)
            if match:
                groups = match.groups()

                course_id = groups[0].strip()
                course_name = groups[1].strip()
                credits_str = groups[2].strip()
                # LT_factor = groups[3].strip() # Bỏ qua
                # TH_factor = groups[4].strip() # Bỏ qua
                theory_hours_str = groups[5].strip()
                project_hours_str = groups[6].strip()
                # Thao_luan_hours = groups[7].strip() # Bỏ qua
                practice_hours_str = groups[8].strip()
                # HD_tu_hoc_hours = groups[9].strip() # Bỏ qua
                # Hoc_ky = groups[10].strip() # Bỏ qua
                prereq_tien_quyet_str = groups[11].strip()
                prereq_hoc_truoc_str = groups[12].strip()

                prerequisite_codes = self.parse_prerequisites(prereq_tien_quyet_str, prereq_hoc_truoc_str)

                parsed_courses_data.append({
                    'course_id': course_id,
                    'course_name': course_name,
                    'credits': self.safe_int_cast(credits_str),
                    'theory_hours': self.safe_int_cast(theory_hours_str),
                    'practice_hours': self.safe_int_cast(practice_hours_str),
                    'project_hours': self.safe_int_cast(project_hours_str),
                    'prerequisite_codes': prerequisite_codes
                })
            elif line and not line.startswith(('I.', 'II.', 'Tc', 'STT', 'LT	TH', 'Kiến thức')):
                # In ra các dòng không khớp để debug nếu cần, loại trừ các dòng header/phân mục đã biết
                self.stdout.write(self.style.WARNING(f"Skipping non-data line or misformatted line: {line}"))

        with transaction.atomic():
            self.stdout.write("Deleting existing courses (optional, for clean slate)...")
            # Course.objects.all().delete() # Bỏ comment nếu muốn xóa tất cả dữ liệu cũ mỗi lần chạy

            self.stdout.write("Creating/Updating Course objects (Phase 1)...")
            for data in parsed_courses_data:
                course, created = Course.objects.update_or_create(
                    course_id=data['course_id'],
                    defaults={
                        'course_name': data['course_name'],
                        'credits': data['credits'],
                        'theory_hours': data['theory_hours'],
                        'practice_hours': data['practice_hours'],
                        'project_hours': data['project_hours'],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created course: {course.course_id} - {course.course_name}"))
                else:
                    self.stdout.write(f"Updated course: {course.course_id} - {course.course_name}")

            self.stdout.write("Setting up prerequisites (Phase 2)...")
            for data in parsed_courses_data:
                try:
                    current_course = Course.objects.get(course_id=data['course_id'])
                    current_course.prerequisites.clear()  # Xóa các prerequisite cũ trước khi thêm mới

                    added_prereqs = []
                    for prereq_code in data['prerequisite_codes']:
                        prereq_code_cleaned = prereq_code.strip()
                        if not prereq_code_cleaned:
                            continue
                        try:
                            prerequisite_course = Course.objects.get(course_id=prereq_code_cleaned)
                            current_course.prerequisites.add(prerequisite_course)
                            added_prereqs.append(prereq_code_cleaned)
                        except Course.DoesNotExist:
                            self.stdout.write(self.style.WARNING(
                                f"Prerequisite course with ID '{prereq_code_cleaned}' not found for '{current_course.course_id}'."
                            ))
                    if added_prereqs:
                        self.stdout.write(f"Added prerequisites {added_prereqs} for {current_course.course_id}")

                except Course.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f"Course with ID '{data['course_id']}' not found during prerequisite setup. This should not happen."
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error setting prerequisites for {data['course_id']}: {e}"))

        self.stdout.write(self.style.SUCCESS('Successfully populated course data.'))
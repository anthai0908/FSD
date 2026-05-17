# Hệ thống Đăng ký Môn học FSD

Ứng dụng đăng ký môn học dành cho sinh viên, hỗ trợ cả giao diện desktop Tkinter và giao diện web.
Hệ thống có các chức năng đăng ký tài khoản, đăng nhập, đăng ký môn học, xóa môn học, hiển thị điểm, và hỗ trợ tư vấn học tập / chat bằng DeepSeek.

## Tính năng

- Đăng nhập và đăng ký sinh viên
- Đăng ký và xóa môn học
- Tính điểm trung bình và xếp loại
- Tư vấn học tập và chat bằng DeepSeek
- Phiên bản GUI desktop
- Phiên bản web đồng bộ và web bất đồng bộ
- Bảng điều khiển quản trị trong bản web async

## Cấu trúc dự án

- `GUI.py` - điểm vào cho ứng dụng Tkinter
- `WebApp.py` - điểm vào cho web HTTP đồng bộ
- `AsyncWebApp.py` - điểm vào cho web async bằng FastAPI
- `Services.py` - lớp xử lý nghiệp vụ và AI
- `Database.py` - lớp truy cập dữ liệu
- `models.py` - mô hình SQLAlchemy và khởi tạo SQLite
- `migrate_csv_to_orm.py` - chuyển dữ liệu CSV sang SQLite
- `students_data.csv` - dữ liệu mẫu
- `run_gui.sh` - chạy ứng dụng desktop
- `run_web.sh` - chạy web đồng bộ
- `run_async_web.sh` - chạy web async

## Yêu cầu

- Python 3.10+
- `pip`
- macOS là môi trường phù hợp cho các script `.sh` vì chúng dùng `open`
- Tính năng AI cần `DEEPSEEK_API_KEY` hợp lệ

## Cài đặt

Tạo và kích hoạt virtual environment, sau đó cài đặt thư viện:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Nếu muốn dùng script Tkinter mặc định của dự án, hãy tạo môi trường `.venv-tk`:

```bash
python -m venv .venv-tk
source .venv-tk/bin/activate
pip install -r requirements.txt
```

## DeepSeek API Key

Ứng dụng đọc `DEEPSEEK_API_KEY` từ:

- biến môi trường hiện tại
- file `.env` ở thư mục gốc dự án

Ví dụ:

```env
DEEPSEEK_API_KEY=your_api_key_here
```

## Chạy ứng dụng

### GUI desktop

```bash
./run_gui.sh
```

### Web đồng bộ

```bash
./run_web.sh
```

Mở:

```text
http://127.0.0.1:8000/login
```

### Web bất đồng bộ

```bash
./run_async_web.sh
```

Mở:

```text
http://127.0.0.1:8000/login
```

## Tài khoản mẫu

- Quản trị viên: `admin` / `admin`
- Sinh viên mẫu: `zhuhang.li@university.com` / `Zhuhangli123`

## Cơ sở dữ liệu

Dự án sử dụng SQLite và sẽ tự tạo file `students.db`.

Nếu muốn import dữ liệu mẫu từ CSV vào database, chạy:

```bash
python migrate_csv_to_orm.py
```

## Ghi chú

- Giao diện desktop dùng các nút bấm để hiển thị văn bản vì giới hạn render Tk trong môi trường hiện tại.
- Phiên bản web lưu session trong bộ nhớ, nên khi khởi động lại ứng dụng thì session sẽ mất.
- Nếu chạy trên Linux hoặc Windows, hãy chạy trực tiếp file Python thay vì dùng script `.sh`.

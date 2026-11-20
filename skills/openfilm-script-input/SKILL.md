---
name: openfilm-script-input
description: "Đọc và nghiệm thu thư mục chứa 7 file kịch bản từ plugin Viết Lách trước khi dựng hoạt hình; giữ nguyên file nguồn, kiểm tra CSV/Markdown, tạo input manifest và báo mâu thuẫn theo mã cảnh."
---

# Cổng P07: nhập 7 tệp kịch bản, không viết lại câu chuyện

Chỉ làm **sau P00–P06** và khi người dùng đã đặt nguồn thực vào `VIDEO_HOAT_HINH_WORKSPACE`. Người dùng chỉ đưa ảnh danh sách filename chưa đủ để giả định đã có file trên máy. Sau khi được cấp quyền đọc đúng `SOURCE_DIR`, xác nhận tệp thực và đọc hết nội dung; không suy diễn từ tên file hay ảnh.

## Đúng 7 tài liệu đầu vào (phân biệt hoa-thường theo tên logic, giữ nguyên tên thật)

| File | Mục đích riêng |
|---|---|
| `KICH_BAN_HOAN_CHINH.md` | Tài liệu tổng hợp nền tảng để hiểu mạch truyện |
| `COT_TRUYEN.md` | Diễn biến, cao trào, kết thúc |
| `NHAN_VAT.md` | Hồ sơ tính cách, diện mạo, tính nhất quán nhân vật |
| `LOI_THOAI.md` | Lời thoại gốc và chỉ dẫn nhân vật/giọng kể |
| `DANH_SACH_CANH.csv` | ID cảnh, mô tả, thời lượng, timecode theo **header thực tế** |
| `HUONG_DAN_HINH_ANH_AM_THANH.md` | Camera, bối cảnh, hành động, âm nhạc và SFX |
| `BAO_CAO_NGHIEM_THU.md` | Kiểm định kịch bản từ công đoạn trước; không thay thế QC render |

Tên thư mục chứa các tệp **không cố định**; nếu nằm ở root workspace, dưới `du-lieu-kich-ban` hoặc tên khác thì dùng đường dẫn user cung cấp/được phép, không tự dời. Đọc nguyên bản ở chế độ read-only, tính SHA-256/size/encoding, giữ BOM có thể có; không dùng source làm đích ghi. CSV dùng UTF-8-sig và `csv` parser có quy tắc escape; kiểm tra delimiter dấu phẩy/chấm phẩy/Tab dựa trên dữ liệu thật. Header không đúng kỳ vọng thì trình ánh xạ cột để duyệt, không đoán cứng. Thời lượng ước tính từ CSV khác WAV thật: phân biệt `estimated` và `verified`.

## Quy tắc hòa giải (không tự sửa dữ liệu)

- So sánh `KICH_BAN_HOAN_CHINH` với 6 file chuyên biệt theo domain; khi có xung đột, đưa chính xác cặp file/vị trí/dòng/cảnh liên quan và hỏi người dùng quyết định, **không tự mặc định cái nào mới nhất**.
- `DANH_SACH_CANH.csv` là bảng timeline đầu vào **sau khi xác minh header**; không được tự tạo thời lượng, ID, lời thoại hay nhân vật mới để lấp chỗ trống. Nếu người dùng đồng ý bổ sung, lưu bản sửa **trong `projects/<film-id>/source-working/`**, không ghi đè 7 file gốc.
- `BAO_CAO_NGHIEM_THU.md` chỉ đánh giá chất lượng kịch bản; đọc trạng thái PASS/FAIL bên trong tài liệu nếu có, không suy ra P07/P20 PASS nếu file tồn tại.
- Đối chiếu các mốc: mã cảnh trong CSV ↔ phần thoại ↔ mô tả góc máy ↔ nhân vật; xác nhận tổng thời lượng, shot overlap/gap, tên và các chi tiết lặp lại. Nếu thiếu nội dung then chốt, đánh dấu `BLOCKED` trước P09.

## Kết quả P07

1. `reports/SOURCE_FILES_MANIFEST.json`: từng file, path, bytes, sha256, encoding, ghi nhận thời điểm/thiết bị thực; không bịa SHA.
2. `reports/INPUT_AUDIT.md`: đủ/thiếu/không đọc được, bảng mapping CSV, vấn đề theo mức độ, đề xuất sửa theo đúng mã cảnh, kết luận PASS/FAIL/BLOCKED.
3. `reports/SCRIPT_TO_PRODUCTION_MAP.md`: mapping từ từng phần nguồn sang `shotId`, `characterId`, `dialogueId`, assets và FilmData; nội dung này là dự kiến cho đến P09.
4. Checkpoint P07 và danh sách phê duyệt sửa mâu thuẫn nếu có; trình cho người dùng duyệt trước P08.

Xem `references/SEVEN_FILES_CHECKLIST.md` và `references/audit_seven_files.py` (script chỉ đọc, stdlib Python; kết quả chỉ chứng minh file có/parse được, **không thay thế** việc hiểu nội dung toàn bộ 7 tệp).

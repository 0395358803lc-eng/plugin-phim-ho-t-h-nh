> v1.14.0: FINISH_FIRST_USER_REVIEW ưu tiên. Đây là công thức kỹ thuật/tham khảo; mọi đánh giá thẩm mỹ chỉ theo yêu cầu người dùng, mọi cổng QC legacy không chặn V01. OpenFilm CLI-first, GUI tùy chọn.

# 7 tệp đầu vào → FilmData: bảng đối chiếu P07

| Kiểm tra | Tệp liên quan | Evidence / hành động nếu lỗi |
|---|---|---|
| 7 tệp thực tồn tại, đọc hết được | Tất cả | Path, SHA256, bytes, UTF-8/CSV parser; không suy ra có file từ ảnh |
| Mạch truyện có mở/giữa/kết, các cảnh tương ứng | KICH_BAN_HOAN_CHINH ↔ COT_TRUYEN ↔ DANH_SACH_CANH | Ghi khác biệt theo file + đoạn nguồn |
| Nhân vật hiện diện và hành vi nhất quán | NHAN_VAT ↔ KICH_BAN ↔ LOI_THOAI | Mã nhân vật, tên, cảnh, xung đột mô tả |
| Lời thoại gắn đúng người/cảnh | LOI_THOAI ↔ DANH_SACH_CANH | Transcript gốc bất biến, gắn mã câu riêng sau P09 |
| CSV header, delimiter, duration, timecode | DANH_SACH_CANH | Ghi tên cột nguyên bản, không mặc định schema hoặc bịa unit thời gian |
| Góc máy/bối cảnh/SFX theo cảnh | HUONG_DAN_HINH_ANH_AM_THANH ↔ danh sách cảnh | Shot camera map và asset need list |
| Kết quả nghiệm thu cũ có thật và hợp lệ | BAO_CAO_NGHIEM_THU | Nêu các issue chưa sửa; đây là QA *script*, không phải QC video |

**Quy tắc bất biến:** source directory giữ nguyên; mọi file sản xuất nằm dưới `projects/<film-id>/` và `reports/`. Nếu `LOI_THOAI.md` không có mã scene hoặc CSV không có cột nhận diện, đánh dấu mapping `NEEDS_REVIEW`, yêu cầu duyệt ánh xạ; không giả định `C001` tương ứng câu đầu tiên.

**Quy tắc phê duyệt P07:** được đọc file trong thư mục cho phép; việc tạo working copy/đổi nội dung/giải quyết mâu thuẫn cần người dùng đồng ý và log hành động. Khi P07 không đầy đủ, chưa chuyển P08–P21.

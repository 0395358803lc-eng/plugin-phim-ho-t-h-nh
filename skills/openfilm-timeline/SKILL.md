---
name: openfilm-timeline
description: "Biên tập timeline OpenFilm: trim, split, ghép clip, track, speed, âm lượng, phụ đề, soundtrack, chỉnh override và export edit khi có runtime."
---

# Biên tập OpenFilm timeline

Đọc `openfilm-dinh-dang` trước; track trong `film.html` là các `<section>`, theo thứ tự trên xuống, track đầu được compositing ở trên. Clip `<iframe>`, `<img>`, `<video>`, `<audio>` có `at`, `src` và `#t=in,out`, `id`, `speed`, `volume`.

## Nguyên tắc thao tác

1. Chụp trạng thái/log hoặc lưu bản sao phục hồi trong thư mục dự án khi được phép; đọc lại `film.html` **ngay trước** mọi ghi vì người dùng có thể chỉnh trong Studio song song.
2. Không sửa track `locked`. Không ghi đè `overrides`, `size` và những chỉnh sửa người dùng không yêu cầu. Nếu sửa clip bằng API Studio cần đọc revision và xử lý conflict theo API thực tế, không giả định an toàn khi ghi raw file.
3. Cắt một file media bằng nhiều đoạn tham chiếu `#t=in,out`, không tự nhân bản/transcode file gốc. Điều chỉnh tốc độ bằng `speed`, âm lượng bằng `volume`. Khi thay đổi vị trí cảnh, dời sound đúng time offset.
4. Với chồng hình/text/PIP, dùng track riêng. Không để clip trùng thời gian trên cùng track. Quy tắc đường tiếng và caption phải đi theo thời gian thực.
5. Khi người dùng trỏ chính xác, phản hồi với link `film.html#t=...` hoặc `film.html#clip-id` chỉ nếu file thực sự tồn tại trong project.
6. Chỉ export round-trip sang NLE khác nếu phiên bản Studio thực đang có tính năng đó; ZIP mô tả hỗ trợ Final Cut Pro/Premiere/DaVinci Resolve nhưng không xác thực lệnh CLI export cụ thể. Sử dụng UI/Help chính thức của phiên bản cài.

## QC

Không mất đầu/cuối thoại, không clip trống/đen ngoài ý đồ, cắt theo nhịp, không lỗi tốc độ tiếng, không track vô tình tắt, độ dài âm nhạc đủ, captions có đúng thời điểm. Sau thay đổi chạy `openfilm look` khi có runtime rồi xem file kết quả.

## FilmData v1.4: one timebase

Mỗi shot/dial nằm trong `[startFrame,endFrame)` theo `film.json`; OpenFilm dùng giây `t=frame/fps`, Remotion dùng integer frame. Khi VieNeu sinh WAV, dùng FFprobe cập nhật timing có kiểm chứng; không dùng đồng thời hai master timeline. Trước export/handoff chạy `openfilm-filmdata/references/validate_filmdata.py`, kiểm asset và kiểm tra `openfilm-hybrid-master` để xác định engine xuất cuối.

## v1.8.0: timeline đã tồn tại từ P09

`openfilm/film.html` được khởi tạo từ FilmData ở P09.06, tham chiếu scene placeholder từng shot và mốc frame đã xác thực. P14/P15 thay page cảnh bằng code thật; P16 kiểm project/preview không còn placeholder và không có đứt cảnh. P17 mở **film.html đã có**, kiểm hash, locked tracks và Studio overrides, thêm track WAV/VTT/SFX/nhạc và sửa cut có duyệt; nếu film.html mất phải chặn/khôi phục từ checkpoint đã duyệt chứ không viết mới lén. Chỉ dùng lệnh OpenFilm theo runtime profile đã xác minh.

## OpenFilm CLI là đường điều khiển v1.9.0

Mọi `look`, `render`, `open` được gọi qua absolute CLI đã xác minh với cwd project chứa `film.html`; sau khi cập nhật timeline P17, kiểm `openfilm look` trên nhiều mốc. Chỉ cho phép `openfilm open` mở Studio tùy chọn sau phê duyệt; Desktop không thay CLI hoặc bản cuối. Đọc `openfilm-cli-execution` trước chỉnh sửa.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate

M5 chỉ QC hình timeline smoke khi ChatGPT đã nhận ảnh frame trích từ **smoke MP4 thực** sau render, không dùng ảnh scene trước compositing. M6/M7 phải xem từ bản draft/master tương ứng. Render hash đổi => yêu cầu xem lại. Xem `openfilm-visual-inspection`.

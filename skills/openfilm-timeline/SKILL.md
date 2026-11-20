---
name: openfilm-timeline
description: "Biên tập timeline OpenFilm: trim, split, ghép clip, track, speed, âm lượng, phụ đề, soundtrack, chỉnh override và export edit khi có runtime."
---

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.



# Biên tập OpenFilm timeline

Đọc `openfilm-dinh-dang` trước; track trong `film.html` là các `<section>`, theo thứ tự trên xuống, track đầu được compositing ở trên. Clip `<iframe>`, `<img>`, `<video>`, `<audio>` có `at`, `src` và `#t=in,out`, `id`, `speed`, `volume`.

## Nguyên tắc thao tác

1. Chụp trạng thái/log hoặc lưu bản sao phục hồi trong thư mục dự án khi được phép; đọc lại `film.html` **ngay trước** mọi ghi vì người dùng có thể chỉnh trong Studio song song.
2. Không sửa track `locked`. Không ghi đè `overrides`, `size` và những chỉnh sửa người dùng không yêu cầu. Nếu sửa clip bằng API Studio cần đọc revision và xử lý conflict theo API thực tế, không giả định an toàn khi ghi raw file.
3. Cắt một file media bằng nhiều đoạn tham chiếu `#t=in,out`, không tự nhân bản/transcode file gốc. Điều chỉnh tốc độ bằng `speed`, âm lượng bằng `volume`. Khi thay đổi vị trí cảnh, dời sound đúng time offset.
4. Với chồng hình/text/PIP, dùng track riêng. Không để clip trùng thời gian trên cùng track. Quy tắc đường tiếng và caption phải đi theo thời gian thực.
5. Khi người dùng trỏ chính xác, phản hồi với link `film.html#t=...` hoặc `film.html#clip-id` chỉ nếu file thực sự tồn tại trong project.
6. Chỉ export round-trip sang NLE khác nếu phiên bản Studio thực đang có tính năng đó; ZIP mô tả hỗ trợ Final Cut Pro/Premiere/DaVinci Resolve nhưng không xác thực lệnh CLI export cụ thể. Sử dụng UI/Help chính thức của phiên bản cài.

## Kiểm tra kỹ thuật; đánh giá thẩm mỹ chỉ khi user yêu cầu

Không mất đầu/cuối thoại, không clip trống/đen ngoài ý đồ, cắt theo nhịp, không lỗi tốc độ tiếng, không track vô tình tắt, độ dài âm nhạc đủ, captions có đúng thời điểm. Sau thay đổi chạy `openfilm look` khi có runtime rồi xem file kết quả.

## FilmData v1.4: one timebase

Mỗi shot/dial nằm trong `[startFrame,endFrame)` theo `film.json`; OpenFilm dùng giây `t=frame/fps`, Remotion dùng integer frame. Khi VieNeu sinh WAV, dùng FFprobe cập nhật timing có kiểm chứng; không dùng đồng thời hai master timeline. Trước export/handoff chạy `openfilm-filmdata/references/validate_filmdata.py`, kiểm asset và kiểm tra `openfilm-hybrid-master` để xác định engine xuất cuối.

## v1.8.0: timeline đã tồn tại từ P09

`openfilm/film.html` được khởi tạo từ FilmData ở P09.06, tham chiếu scene placeholder từng shot và mốc frame đã xác thực. P14/P15 thay page cảnh bằng code thật; P16 kiểm project/preview không còn placeholder và không có đứt cảnh. P17 mở **film.html đã có**, kiểm hash, locked tracks và Studio overrides, thêm track WAV/VTT/SFX/nhạc và sửa cut có duyệt; nếu film.html mất phải chặn/khôi phục từ checkpoint đã duyệt chứ không viết mới lén. Chỉ dùng lệnh OpenFilm theo runtime profile đã xác minh.

## OpenFilm CLI là đường điều khiển v1.9.0

Mọi `look`, `render`, `open` được gọi qua absolute CLI đã xác minh với cwd project chứa `film.html`; sau khi cập nhật timeline P17, dùng `openfilm look` nếu cần chẩn đoán. Chỉ cho phép `openfilm open` mở Studio tùy chọn sau phê duyệt; Desktop không thay CLI hoặc bản cuối. Đọc `openfilm-cli-execution` trước chỉnh sửa.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate


P17 hoàn thiện timeline từ cảnh, WAV, nhạc/SFX và phụ đề. P18 smoke là tùy chọn, có thể SKIPPED có lý do; chuyển P19 render V01 khi timeline dùng được.

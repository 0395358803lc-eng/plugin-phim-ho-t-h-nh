# Đánh giá bản render theo yêu cầu — v1.14.1

Chạy khi user yêu cầu kiểm chất lượng bản phim. Kiểm file tồn tại/đường dẫn/hash/giải mã/stream là phần kỹ thuật sản xuất thường lệ ở production playbook; không cần gọi bộ QC này để được giao V01.

| Phần cần xem | Phương pháp | Giới hạn cần ghi |
|---|---|---|
| Cấu trúc và nội dung | Đối chiếu film.json, shot list, relative media, duration | Metadata không chứng minh hình đẹp |
| Hình và phụ đề | Frame trích từ MP4 đúng version; xem chữ/crop/continuity | Frame mẫu không thay xem toàn phim |
| Chuyển động | Xem đoạn được yêu cầu hoặc seek cùng t | Cần clip thực nếu đánh giá nhịp |
| Audio | Decode và nghe bản thật nếu tool cho phép | Decode không chứng minh phát âm tự nhiên |
| Màu | Đối chiếu shot liền nhau, đo nếu có công cụ | Không tự đổi palette theo sở thích |
| Bàn giao | Video, captions, source, manifest, hash | Không tự xuất bản hoặc chấp nhận thay user |

## Công cụ

OpenFilm look/render dùng CLI đã cài và --help của đúng phiên bản. Look tại timestamp, khoảng thời gian, contact sheet hoặc loudness chỉ dùng nếu runtime hỗ trợ. Không mặc định các cờ --4k/--blur/--alpha tồn tại. Render trong cwd có film.html, output path chưa tồn tại, giữ argv/log/exitCode.

FFprobe đọc streams/codec/fps/resolution/duration/sample rate; FFmpeg decode kiểm file hỏng. Loudness -14 LUFS chỉ là profile tham khảo nếu phù hợp đích, không phải chuẩn bắt buộc mọi phim. Không render lại master trùng nội dung chỉ để có tên FINAL_MASTER.mp4.

Nếu yêu cầu đánh giá VieNeu, nghe WAV/MP4 thật và nêu rõ phần đã nghe. Khi không có khả năng nghe, cung cấp file và đánh dấu nhận xét giọng là NOT_VERIFIED. Không ép user nghe/duyệt từng câu trước khi dựng.

## Báo cáo và sửa

Mỗi nhận xét có target/shot/time, source hash, evidence path và PASS/FAIL/NOT_VERIFIED cho phạm vi được yêu cầu. Không giả playback từ screenshot, không giả nghe từ log. Lỗi decode được xử lý như FAILED_TECHNICAL của file; nhận xét thẩm mỹ chuyển feedback scene/audio/subtitle/effect.

V01 đã bàn giao được giữ nguyên. Bản sửa V02 có đường dẫn và SHA mới, history liên kết V01. Không tự mở QC20, không khóa P21 vì thiếu Visual report, không tự ghi USER_ACCEPTED. Remotion Master dùng Remotion encode theo profile đã chọn, OpenFilm vẫn CLI cho phần previs; không chuyển Desktop làm fallback.

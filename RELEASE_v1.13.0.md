# Video-hoạt-hình v1.13.0 — Image ZIP handoff

Khi ChatGPT sinh ảnh trong **phạm vi đã duyệt** và ảnh nằm trong file thực ở sandbox, tự động đóng gói các PNG thành một file ZIP tải về gồm `projects/<film>/...png`, manifest SHA-256 và hướng dẫn giải nén. Người dùng tải, giải nén vào **workspace root trên Windows**, rồi xác nhận để ChatGPT kiểm SHA từ file remote và thực sự đọc pixel. Giữ `VISUAL_BLOCKED`/`AWAITING_...` cho đến khi có chứng cứ. Không dùng ảnh chat hoặc hình có chữ QC làm biên bản.

- Thêm skill `openfilm-image-zip-handoff` và script Python stdlib `image_handoff.py` có `pack` và `verify`.
- ZIP có kiểm PNG signature, CRC, chunk, dimensions, duplicate names, traversal và relative workspace paths; script kiểm lại ZIP sau khi ghi. Không chạy lệnh ngoài scope của người dùng trên Windows.
- Giữ 8 macro M0–M7, 99 packet, cổng phê duyệt hiện hữu, Remotion/OpenFilm và GPU-first VieNeu. Không thay đổi trạng thái phim hay tự mở P11.
- Không tuyên bố mọi image_gen output đều được mount file: khi không có byte ảnh thật trong sandbox, báo `IMAGE_BINARY_UNAVAILABLE`, không tạo ZIP giả.

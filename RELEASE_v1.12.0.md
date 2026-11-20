# Video-hoạt-hình v1.12.0 — Mandatory Visual Inspection & Quality Gate

- Nguồn v1.11.0 được nâng cấp, không tạo plugin mới; bảo toàn 8 macro M0–M7, 99 packet nội bộ và 31 skill cũ.
- Kỹ năng mới `openfilm-visual-inspection` yêu cầu ChatGPT thật sự nhận ảnh multimodal, không chỉ CLI/log/JSON/FFprobe.
- M2: xem storyboard/characters/background/assets thực; M4: frame OpenFilm CLI look từng shot; M5: smoke MP4; M6: draft MP4; M7: FINAL_MASTER.mp4 mới.
- Công cụ sample_render_frames.py trích ảnh MP4 với FFmpeg/FFprobe đã được duyệt; chỉ tạo ảnh và extraction log, không tự PASS. Các ảnh được đọc bằng Remote Desktop Commander read_file/read_multiple_files hoặc user upload, sau đó ChatGPT mô tả riêng và ghi report.
- Cổng `validate_visual_qc.py` kiểm source/media/image hashes, PNG decode, target/role coverage, extraction provenance và metadata receipt. `validate_macro_event.py` đọc lại report thực từ workspace và chặn ACCEPT M2/M4/M5/M6/M7 khi thiếu hoặc stale. Mọi thay đổi source/render yêu cầu kiểm lại.
- Không thêm nút phê duyệt từng ảnh. Các phê duyệt đặc biệt và VieNeu GPU-first, OpenFilm CLI-first không đổi. Chưa kiểm thử chạy workflow end-to-end trên Windows; mới có kiểm thử code và sampler FFmpeg trên môi trường thử nghiệm.
- Không giả định Python có thể chứng minh ChatGPT đã thật sự nhìn ảnh; chỉ mô hình sau khi nhận ảnh hiển thị mới được xác nhận receipt. Trường hợp chỉ text/binary không được truyền thị giác -> VISUAL_BLOCKED. Không tuyên bố xem liên tục toàn bộ phim từ frame mẫu.

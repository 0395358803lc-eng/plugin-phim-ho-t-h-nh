> v1.14.0: FINISH_FIRST_USER_REVIEW ưu tiên. Đây là công thức kỹ thuật/tham khảo; mọi đánh giá thẩm mỹ chỉ theo yêu cầu người dùng, mọi cổng QC legacy không chặn V01. OpenFilm CLI-first, GUI tùy chọn.

Chỉ dùng khi người dùng chủ động yêu cầu QC. Không có quyền chặn macro hoặc bàn giao.

# Quy trình lấy ảnh thật, nhận bằng mắt mô hình, kiểm render

1. **Xác minh source** `film.json`, các `shots[].id/startFrame/durationInFrames`, bản render MP4 chính xác và hash SHA256. Nguồn file MP4 smoke/draft/master chỉ được dùng khi OpenFilm CLI/Remotion renderer đã tạo thành công và QC kỹ thuật tồn tại. Dùng OpenFilm CLI `look` để trích frame cảnh M4; không giả định syntax lệnh chưa xác nhận với `--help`.
2. **M2** hình raster storyboard, nhân vật và nền; nếu SVG thì chuyển sang PNG bằng công cụ đã được duyệt. Không coi file SVG text hoặc mô tả prompt là bằng chứng đã xem.
3. **M4** mỗi shot tối thiểu START/Q1/MID/Q3/END, thêm trước/sau cut. Dùng `openfilm look` và công cụ đọc ảnh nhận được; nếu CGI/WebGL chuyển động nhanh, lấy thêm contact sheet dày hoặc các frame liền kề. Random seek test kỹ thuật riêng.
4. **M5–M7** trích từ **file MP4 output** bằng FFmpeg, đúng source sha; script `sample_render_frames.py` tạo PNG và extraction log ở `qc/visual/Mx/`, không tự ghi nhận xét, không cho PASS. M5 five roles trên 5s; M6/M7 ba roles mỗi shot đã materialize từ `film.json`. Dùng `read_multiple_files` theo đợt tránh giới hạn dung lượng; phải có multimodal image thực. Nếu quá nhiều cảnh, checkpoint trong cùng macro rồi tiếp tục, không hiển thị nút duyệt từng ảnh.
5. **Trong một lượt ChatGPT**: nhìn và chú thích từng ảnh: chủ thể, bố cục, tính nhất quán, chi tiết sai/hỏng, đối chiếu thiết kế được duyệt; nếu không thấy, dừng chứ không bịa. Với contact sheet, zoom/đọc ảnh riêng khi không đủ rõ. Theo shot ID và role ghi report; sửa issues trong phạm vi được duyệt, trích và nhìn ảnh sửa lại.

## Lưu ý

- Kết quả `FFprobe`/không lỗi khi render KHÔNG thay thế nhìn ảnh; receipt có log mà không có multimodal image = BLOCKED.
- Hình từ chính video có thể không chứng minh video chuyển động mượt; yêu cầu dãy frame liền kề hoặc video xem được ở bước nhịp chuyển động. Không kết luận đã xem/nghe toàn bộ phim từ 3 frame/shot.
- Tiếng nói VieNeu cần QC WAV/âm thanh riêng, không được coi `VISUAL_PASS` là `VOICE_AUDIO_QC`.
- Không chuyển ảnh video lên dịch vụ mới không được duyệt; Remote Desktop Commander image reads hoặc ảnh người dùng gửi là hai tuyến được phép.

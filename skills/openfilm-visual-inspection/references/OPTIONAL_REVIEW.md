# Đánh giá thị giác theo yêu cầu — v1.14.1

Chỉ chạy khi người dùng chủ động yêu cầu đánh giá hình ảnh. Không tạo cổng Visual PASS trước render/bàn giao, không thêm approval từng frame/shot. Thất bại trong việc truyền ảnh chỉ làm phần đánh giá chưa xác minh; không tự đổi trạng thái file video dùng được.

## Chọn bằng chứng

Ghi rõ phạm vi user yêu cầu: storyboard/asset, cảnh source hay video đã render. M2 dùng ảnh storyboard/nhân vật/bối cảnh thật. Cảnh source có thể dùng OpenFilm CLI look nếu version hỗ trợ. Đánh giá video phải trích từ đúng MP4/version bằng FFmpeg, không dùng ảnh HTML để thay.

Chọn mốc theo mục tiêu: đầu/giữa/cuối cảnh, cut boundary, hành động nhanh, continuity hoặc frame cụ thể người dùng chỉ ra. Ghi danh sách mốc đã xem; không áp sẵn năm ảnh cho mọi cảnh và không tuyên bố xem toàn phim từ một contact sheet. Lưu source path/hash, shotId, frameIndex/time, image path/hash và lệnh trích.

## Nhìn ảnh thật và ghi nhận xét

Dùng view_image cho file local hoặc connector trả image content. Với functions.exec phải chuyển image block bằng image(part), không chỉ in base64/text/success. Nếu tool không truyền pixel thì ghi NOT_VERIFIED cho phần nhìn ảnh; chỉ nhờ người dùng gửi ảnh khi cần để trả lời yêu cầu đánh giá đó.

Sau khi thực sự nhận ảnh, ghi observation riêng: chủ thể/bố cục đang thấy, crop, nhân vật, tỷ lệ, ánh sáng, chữ tiếng Việt, continuity, khác biệt storyboard. Không lấy chữ “PASS” vẽ trong ảnh làm bằng chứng. Phân biệt lỗi kỹ thuật (đen do media hỏng) với nhận xét thẩm mỹ (muốn nhân vật lớn hơn).

Báo cáo có request/scope, source hash, targets, observedFrames, observation, issues và limitations. validate_visual_qc.py chỉ đối chiếu bytes/hash/provenance của schema legacy khi cần; nó không chứng minh mô hình đã thấy pixel. Không tạo hostImageEvidence giả để qua validator.

## Sửa và hiệu lực báo cáo

Issue gắn targetId, frame/time, ảnh bằng chứng, mô tả và thay đổi đề nghị. Chỉ sửa trong phạm vi đã cấp; nếu ngoài scope thì trình phần mới. Source/render hash đổi thì đánh dấu nhận xét cũ không áp dụng cho bản mới. Giữ ảnh/báo cáo cũ như lịch sử; không gán Visual PASS cho V02 dựa trên V01.

Kết quả tùy chọn PASS/FAIL/NOT_VERIFIED thuộc báo cáo đánh giá, không đồng nghĩa OUTPUT_READY/USER_ACCEPTED. Chấp nhận phim vẫn là phản hồi người dùng.

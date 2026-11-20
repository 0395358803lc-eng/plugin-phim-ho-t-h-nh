---
name: openfilm-kich-ban
description: "Chuyển truyện, lời thoại hoặc yêu cầu thành storyboard và shot list cho video hoạt hình; duy trì nhân vật nhất quán, chuẩn bị Canvas OpenFilm."
---

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.



# Kịch bản, nhân vật và storyboard hoạt hình

## Tiếp nhận

Tách văn bản nguồn khỏi đề xuất sáng tạo; không tự sửa ý nghĩa khi chưa được yêu cầu. Phân đoạn thành beat có thời lượng, mục tiêu cảm xúc, câu thoại đúng nguyên văn hoặc tường thuật, hành động quan sát được, góc máy và chuyển động.

## Shot-list tối thiểu

Lưu bảng Markdown/CSV với `shot_id`, `in`, `out`, `duration`, `scene`, `characters`, `action`, `camera`, `dialogue/VO`, `SFX/music`, `subtitle`, `asset_ref`, `transition`, `QC`. Tổng thời lượng phải khớp mục tiêu; chỉ ước tính khi chưa có audio đo được. Mỗi cảnh độc lập một `scenes/<shot_id>.html` hoặc media clip.

## Nhân vật nhất quán

Thiết lập character bible: tên, dáng, trang phục, 3-5 màu cố định, góc nhìn, biểu cảm, đặc điểm không đổi. Nếu Canvas OpenFilm có sẵn, tạo note -> portrait -> fullBody/expressions/turnaround16; nối portrait làm tham chiếu cho mọi cảnh. Không tự tuyên bố công cụ đã sinh ảnh nếu chưa thực hiện.

## Các kiểu hình ảnh

Với HTML/SVG/CSS thuần, tạo hoạt hình 2D, typographic, whiteboard và explainer bằng DOM/SVG/Canvas. Với Three.js/WebGL có sẵn, có thể lập kế hoạch cảnh 3D; khả năng render thực tế phụ thuộc mã và GPU/browser trên máy. Kiểm tra tương thích trước khi hứa 3D photorealistic.

## Gate nghiệm thu

- Kịch bản/beat đầy đủ, không thiếu lời thoại.
- Thời lượng và tỷ lệ khung hình rõ ràng.
- Nhân vật và visual style không drift.
- Danh sách media, giấy phép sử dụng, đầu ra và thiếu sót.

Đọc `openfilm-canvas` cho các thao tác canvas CLI thực; đọc `openfilm-animation` khi chuyển storyboard thành trang cảnh.

## P10 Canvas decision v1.8.0

Thực hiện P10.06 chọn `FILE_STORYBOARD` hoặc `OPENFILM_CANVAS` dựa runtime verified. Nếu dùng Canvas, P10.07 bố trí board được duyệt nhưng không Make nodes tự chạy. Nếu không, lưu storyboard file bình thường, không báo fail. Tham chiếu `openfilm-runtime-control/references/CANVAS_DECISION.md`.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate

M2 cần ChatGPT trực tiếp nhìn ảnh storyboard, nhân vật và bối cảnh đã rasterize, không chỉ đọc mô tả `.md`/SVG text/Canvas JSON. Toàn bộ `visualTargets[M2]` phải phản ánh shot/character/background IDs có thật trong nguồn được duyệt. Nếu chưa chuyển được ảnh vào ChatGPT multimodal, dừng `VISUAL_BLOCKED`, không đánh dấu chất lượng hình ảnh đạt. Xem `openfilm-visual-inspection`.

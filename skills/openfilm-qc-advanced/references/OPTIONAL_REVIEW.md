> v1.14.0: FINISH_FIRST_USER_REVIEW ưu tiên. Đây là công thức kỹ thuật/tham khảo; mọi đánh giá thẩm mỹ chỉ theo yêu cầu người dùng, mọi cổng QC legacy không chặn V01. OpenFilm CLI-first, GUI tùy chọn.

Chỉ dùng khi người dùng chủ động yêu cầu QC. Không có quyền chặn macro hoặc bàn giao.

# Quy trình đánh giá tùy chọn

Chỉ áp dụng khi người dùng yêu cầu đánh giá chất lượng. Không chặn sản xuất hoặc bàn giao V01. Các từ “bắt buộc” dưới đây chỉ ràng buộc báo cáo đánh giá được yêu cầu, không phải tiến độ phim.



# QC nâng cao và smoke 5 giây (N14, N16, N18)

Cần sau `openfilm-filmdata`, `openfilm-audio-subtitles` và `openfilm-render-profiles`. Nguồn 20 mục từ báo cáo đính kèm; xem `references/QC20.md`. **Không đánh dấu PASS nếu chưa có artifact thực**: nguồn mẫu, TSX hoặc lệnh dự kiến không thay thế video đã render.

## Determinism và kiểm thử ở frame bất kỳ

1. Có bản dữ liệu integer frames, cố định seed của random, GSAP timeline paused+seek, Three/R3F transform tính trực tiếp từ frame, VieNeu audio nằm trên timeline riêng.
2. So sánh ít nhất các mốc [0, giữa, cuối-1] và trình tự random `[0, 90, 15, 90, 0]` nếu clip dài đủ. Với OpenFilm dùng `window.film.frame(t)` với `t=frame/fps`; Remotion dùng `useCurrentFrame` và render frame sequence. So sánh pixel trong tolerance/hardware, không đòi bit-identical khác GPU.
3. So sánh shot boundary `endFrame-1` và `next.startFrame`, phát hiện missing media, frame đen/nhảy cảnh.

## Smoke

- **SMOKE-01:** sau khi đã được duyệt và dependencies/runtime đã kiểm, render **5 giây, 150 frames ở 30fps** (hoặc 5*fps theo profile) gồm hình 2D, 3D nếu bật, một WAV mẫu có quyền, phụ đề và SFX/nhạc nếu cần. Output trong `WORKSPACE/renders/smoke/`, không ghi đè nguồn; không `npx` fallback download.
- **SMOKE-02:** dùng FFprobe đo streams, codec, FPS, width/height, duration, sample rate; đọc log; phát video cả hình và tiếng. Chỉ PASS nếu file thực tồn tại và xem/nghe được.
- **SMOKE-03:** đối chiếu sample gốc/timeline. Fail → báo nguyên nhân và xin duyệt phạm vi sửa; không âm thầm tiếp tục master.

## QC 20 điều kiện

Mỗi mục trong `references/QC20.md` có ba trạng thái `PASS/FAIL/BLOCKED` và evidence path/line. Khóa phát hành nếu script chưa khóa, voice chưa nghe, font sai, soundtrack thiếu license, model/texture missing, codec không phù hợp, hoặc QC master thiếu. Bảo toàn SRT, WAV, project source, manifest, logs. Render preview và master cần phê duyệt công đoạn riêng nếu yêu cầu.

## Kết nối P18–P21 v1.5.0

Mọi lần smoke/draft/QC20/master phải ghi bằng chứng từng stage trong `reports/PRODUCTION_STATUS.json` theo `openfilm-checkpoint-approval`. P18 FAIL khóa P19, P20 FAIL khóa P21. P21 PASS chỉ nếu master MP4 thật có FFprobe + phát/quan sát/nghe thật; log render đơn lẻ không chứng minh có video. Bản draft sau sửa phải có revision mới, chỉ invalidate unit/shot/sequence bị ảnh hưởng.

## Hai smoke độc lập v1.8.0

OpenFilm E2E P06 kiểm tra máy/runtime trên project fixture 7s (cảnh + WAV tone + VTT), còn P18 kiểm tra timeline/thành phẩm thực đã tích hợp nhiều shots và VieNeu khi bật. Không gộp PASS hai bài test; FFprobe và kiểm xem/nghe riêng. Khi CLI không khả dụng nhưng GUI đã xác minh, chỉ thử qua GUI sau duyệt, không dùng npx tải hoặc ghi sai trạng thái.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
QC20 ở M6 phải bao gồm trực tiếp đọc frame trích từ **draft MP4** của tất cả `shot_id` được materialize, không chỉ FFprobe/JSON. M7 kiểm lại frame từ **FINAL_MASTER.mp4**; bản draft không thay thế được. Ghi nhận xét thị giác thật và source/image hash, report `qc/visual/M6|M7`, chặn PASS/accept nếu thiếu; xem `openfilm-visual-inspection/SKILL.md`. Không tuyên bố full video playback từ frame sample, QC âm thanh/voice vẫn riêng.

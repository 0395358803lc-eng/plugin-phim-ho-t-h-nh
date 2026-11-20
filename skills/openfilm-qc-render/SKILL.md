---
name: openfilm-qc-render
description: "Đánh giá bản render khi người dùng yêu cầu; đối chiếu hình, thoại, phụ đề, timeline và phiên bản thật."
---

# openfilm-qc-render — v1.14.1

Chỉ kích hoạt khi người dùng yêu cầu phạm vi đánh giá tương ứng. Mặc định FINISH_FIRST_USER_REVIEW hoàn thành và bàn giao V01 trước phản hồi; không đặt QC20/Visual PASS/nghe từng câu thành cổng chuyển macro. Báo cáo đánh giá không cấp quyền và không tự ghi USER_ACCEPTED.

## Phạm vi và phương pháp

Đối chiếu script/FilmData với video đã render. Phân biệt file decode được với chất lượng hình/giọng đã quan sát. Dùng FFprobe/FFmpeg cho metadata và lỗi file; OpenFilm look chỉ nếu CLI đã cài hỗ trợ; nghe/xem thật khi báo đã nghe/xem. Ghi giới hạn nếu host không phát âm thanh hoặc chỉ xem frame mẫu.

Giữ lệnh render, cwd, exit code, stream metadata, video hash và evidence đúng phiên bản. Không render master trùng nội dung hoặc đổi engine để làm báo cáo. Chuyển nhận xét thành feedback scene/audio/subtitle/effect, giữ V01 khi làm V02.

## Thực hiện

Đọc [quy trình chi tiết](references/OPTIONAL_REVIEW.md) và [quyền macro](../openfilm-macro-bundles/SKILL.md). Dùng OpenFilm CLI đã xác minh; Desktop chỉ để xem tùy chọn. Không tải/cài, đổi CPU/provider hoặc mở rộng phạm vi theo yêu cầu đánh giá chung.

Kiểm file kỹ thuật thông thường ở [production playbook](../openfilm-production-p06-p21/references/PRODUCTION_PLAYBOOK.md). File thiếu/hỏng/sai hash cần sửa trước khi bước phụ thuộc sử dụng; nhận xét thẩm mỹ được trả lại người dùng và không biến thành chu kỳ nghiệm thu từng packet.

---
name: openfilm-visual-inspection
description: "Đánh giá hình ảnh khi người dùng yêu cầu: pixel thật, provenance, nhận xét theo shot và giới hạn bằng chứng."
---

# openfilm-visual-inspection — v1.14.1

Chỉ kích hoạt khi người dùng yêu cầu phạm vi đánh giá tương ứng. Mặc định FINISH_FIRST_USER_REVIEW hoàn thành và bàn giao V01 trước phản hồi; không đặt QC20/Visual PASS/nghe từng câu thành cổng chuyển macro. Báo cáo đánh giá không cấp quyền và không tự ghi USER_ACCEPTED.

## Phạm vi và phương pháp

Chọn storyboard/asset, source scene hoặc MP4 đúng phiên bản theo mục tiêu người dùng. Trích ảnh bằng công cụ sẵn có, tính hash rồi đưa pixel thật vào ngữ cảnh nhìn ảnh; không lấy metadata, OCR hoặc base64 text làm bằng chứng đã xem. Nhận xét riêng về bố cục, chữ, nhân vật và continuity; không suy ra xem toàn phim từ vài frame.

Báo cáo đánh giá gắn source hash, shot/time, image hash, observations và issues. Khi đổi source/render, nhận xét cũ không áp cho bản mới. Nếu tool không truyền ảnh, ghi NOT_VERIFIED cho phần đánh giá. Chỉ sửa theo scope hiện có hoặc phản hồi cụ thể.

## Thực hiện

Phân biệt OUTPUT_READY (file dùng được), DELIVERED_FOR_REVIEW (đã giao) và USER_ACCEPTED (người dùng chấp nhận). Đánh giá tùy chọn không thay các trạng thái này. Cài đặt, tải model, GPU→CPU hoặc provider mới cần phê duyệt riêng nếu chưa được cấp trong phiên.

Đọc [quy trình chi tiết](references/OPTIONAL_REVIEW.md) và [quyền macro](../openfilm-macro-bundles/SKILL.md). Dùng OpenFilm CLI đã xác minh; Desktop chỉ để xem tùy chọn. Không tải/cài, đổi CPU/provider hoặc mở rộng phạm vi theo yêu cầu đánh giá chung.

Kiểm file kỹ thuật thông thường ở [production playbook](../openfilm-production-p06-p21/references/PRODUCTION_PLAYBOOK.md). File thiếu/hỏng/sai hash cần sửa trước khi bước phụ thuộc sử dụng; nhận xét thẩm mỹ được trả lại người dùng và không biến thành chu kỳ nghiệm thu từng packet.

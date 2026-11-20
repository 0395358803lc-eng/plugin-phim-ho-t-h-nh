---
name: openfilm-qc-advanced
description: "QC20, determinism, random seek và smoke theo yêu cầu hoặc chẩn đoán kỹ thuật cụ thể."
---

# openfilm-qc-advanced — v1.14.1

Chỉ kích hoạt khi người dùng yêu cầu phạm vi đánh giá tương ứng. Mặc định FINISH_FIRST_USER_REVIEW hoàn thành và bàn giao V01 trước phản hồi; không đặt QC20/Visual PASS/nghe từng câu thành cổng chuyển macro. Báo cáo đánh giá không cấp quyền và không tự ghi USER_ACCEPTED.

## Phạm vi và phương pháp

Dùng phép kiểm phù hợp vấn đề: seed/integer frames, GSAP paused+seek, Three/R3F state từ frame, shot boundary, voice/caption alignment, encode hoặc package. Random seek so cùng frame qua thứ tự khác; smoke là đoạn thử có mục đích, không phải nghĩa vụ trước mọi V01.

QC20 là danh mục tham khảo chỉ khi được yêu cầu. Báo cáo PASS/FAIL/NOT_VERIFIED cho phần đã kiểm, với source/version và evidence. Tone fixture chỉ chứng minh đường render/audio, không thay VieNeu GPU. Giữ bản cũ và hash khi sửa.

## Thực hiện

Đọc [quy trình chi tiết](references/OPTIONAL_REVIEW.md) và [quyền macro](../openfilm-macro-bundles/SKILL.md). Dùng OpenFilm CLI đã xác minh; Desktop chỉ để xem tùy chọn. Không tải/cài, đổi CPU/provider hoặc mở rộng phạm vi theo yêu cầu đánh giá chung.

Kiểm file kỹ thuật thông thường ở [production playbook](../openfilm-production-p06-p21/references/PRODUCTION_PLAYBOOK.md). File thiếu/hỏng/sai hash cần sửa trước khi bước phụ thuộc sử dụng; nhận xét thẩm mỹ được trả lại người dùng và không biến thành chu kỳ nghiệm thu từng packet.

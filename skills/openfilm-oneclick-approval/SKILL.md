---
name: openfilm-oneclick-approval
description: "Hiển thị thao tác tiếp tục sản xuất và đánh giá video sau bàn giao."
---

# openfilm-oneclick-approval — v1.14.1

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.

Nút theo giao diện host: **Tiếp tục sản xuất V01**, **Xem tiến độ**, **Xem video V01**, **Chấp nhận video**, **Yêu cầu chỉnh sửa**. Nút cài đặt/tải model/CPU fallback và các quyền đặc biệt giữ riêng.

Nếu host không có nút thật, dùng lựa chọn văn bản ngắn; không vẽ nút giả hoặc tạo approval receipt. Xem tiến độ/Xem video là đọc, không phê duyệt. Tiếp tục chỉ dùng scope đã duyệt; nếu chưa duyệt thì trình scope cụ thể trước. Chấp nhận video cần video đã giao cùng sự kiện người dùng; yêu cầu chỉnh sửa phải có danh sách mục cần sửa. Không hỏi QC từng packet.

Đọc [openfilm-macro-bundles](../openfilm-macro-bundles/SKILL.md). Validator approval legacy chỉ cho checkpoint cũ.

## Kết nối host và lưu event

Đọc [ONE_CLICK_CONTRACT.md](references/ONE_CLICK_CONTRACT.md) cho bảng action, payload, stale revision và ranh giới quyền. Chỉ dùng callback/API thực đang có; không giả định GenUI tồn tại. Xem tiến độ/video không tăng revision hoặc sinh approval. Không thử chấp nhận trên checkpoint thật chỉ để kiểm thử giao diện.

Nếu host không hỗ trợ nút, liên kết file và câu trả lời trong chat là đường dùng thực. Ghi rõ UI chưa kiểm chứng, không lấy test Python làm bằng chứng đã click trong ChatGPT. Một lần cấp scope nhiều macro được giữ khi tiếp tục, không trình lại 99 packet.

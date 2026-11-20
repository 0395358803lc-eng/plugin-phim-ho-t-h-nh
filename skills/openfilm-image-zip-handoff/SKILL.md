---
name: openfilm-image-zip-handoff
description: "Đóng gói PNG thật thành ZIP và kiểm chứng khi nhập vào Windows workspace."
---

# openfilm-image-zip-handoff — v1.14.0

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.

Khi sinh ảnh trong scope đã duyệt và có byte PNG thật, tự đóng gói ZIP cùng lượt bằng `references/image_handoff.py`. Không tự tạo ảnh mới chỉ vì đang kiểm thử plugin. Dùng đúng filmId, targetId, workspace, đường dẫn và SHA256 nguồn của dự án hiện hành; không sao chép dữ liệu phim mẫu.

1. Tạo spec có handoffId mới, targetWorkspace, images gồm targetId, inputPng, targetRelativePath, sourceTextPath, sourceTextSha256.
2. Chạy `python image_handoff.py pack --spec SPEC.json --output HANDOFF.zip` trong môi trường đang giữ PNG. Script kiểm PNG/ZIP và manifest SHA256. File ảnh phải giải mã được qua bộ kiểm tra kỹ thuật; không chấm thẩm mỹ.
3. Chỉ đưa link tải khi ZIP thật tồn tại. Trạng thái ZIP_READY_FOR_DOWNLOAD / AWAITING_USER_EXTRACTION chưa chứng minh file có trên Windows. Không bịa link sandbox từ tên ảnh trong chat.
4. Hướng dẫn giải nén nội dung vào đúng workspace đã chọn, giữ đường dẫn tương đối; không ghi đè ảnh cũ khi chưa có quyền. ZIP không chứa path tuyệt đối, traversal, symlink hay file ngoài scope.
5. Sau khi có bằng chứng file trên Windows, chạy `python image_handoff.py verify --workspace WORKSPACE --manifest handoffs/HANDOFF_ID/MANIFEST.json` bằng quyền đọc đã có. Đối chiếu hash và kiểm giải mã PNG rồi ghi OUTPUT_READY. Không cần xem/chấm từng ảnh để dựng phim.

Nếu chỉ có ảnh hiển thị mà không truy cập byte: IMAGE_BINARY_UNAVAILABLE. Không tạo ảnh trống/ZIP giả. Nếu user nói đã giải nén nhưng chưa đọc được file: AWAITING_REMOTE_VERIFICATION. Chỉ yêu cầu hỗ trợ chuyển file khi đó là thiếu đầu vào thực tế.

Ví dụ minh họa (không tự áp dụng): filmId `demo-film`, targetId `shot-A`, targetRelativePath `projects/demo-film/assets/shot-A.png`. Thay bằng dữ liệu thật trước khi chạy; không dùng hash placeholder.

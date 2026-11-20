> v1.14.0: FINISH_FIRST_USER_REVIEW ưu tiên. Đây là công thức kỹ thuật/tham khảo; mọi đánh giá thẩm mỹ chỉ theo yêu cầu người dùng, mọi cổng QC legacy không chặn V01. OpenFilm CLI-first, GUI tùy chọn.

# P10.06/07 — Quyết định OpenFilm Canvas

| Điều kiện | Quyết định | Thực thi |
|---|---|---|
| Không yêu cầu Canvas/CLI Canvas chưa verified | `FILE_STORYBOARD` (default) | Tạo storyboard file/ảnh riêng, không đánh dấu lỗi |
| User yêu cầu Canvas, `openCanvas=VERIFIED` bằng evidence, đã phê duyệt ghi board | `OPENFILM_CANVAS` | Dùng lệnh/phương pháp UI *đã kiểm chứng tại P06*, tạo notes, group, references rồi nghiệm thu board thật |
| Canvas không khả dụng | `SKIPPED_CANVAS` | Tiếp tục file storyboard, báo nguyên nhân, không tìm provider TTS khác |

**Nguyên tắc quyền:** `openfilm canvas apply` có thể sửa board; chỉ khi P10.07 được duyệt. Các `node` TTS/voice-over trong skill Canvas upstream là khả năng chung của OpenFilm, không được dùng làm nguồn TTS cho phim dùng VieNeu. Node video/image có thể tạo phí khi bấm `Make`/`Make all`: không bấm; muốn tạo phải duyệt gói, nhà cung cấp và phí riêng. Không bịa `canvas` command nếu Desktop chỉ có UI.

Dữ liệu quyết định tùy chọn `reports/openfilm/CANVAS_DECISION.json`: `{mode, runtimeProfileEvidence, approvalId, reason, boardPath, status}`. Nếu mode file thì `boardPath` có thể null, luôn phải có file storyboard thật để P10 PASS.

**v1.9.0 override:** `OPENFILM_CANVAS` chỉ qua lệnh OpenFilm CLI `canvas`/`canvas apply` đã xác minh. Không fallback Desktop UI để đáp ứng canvas; khi CLI Canvas không hỗ trợ, `FILE_STORYBOARD` là lựa chọn hợp lệ.

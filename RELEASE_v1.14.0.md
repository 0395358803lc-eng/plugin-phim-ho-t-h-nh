# v1.14.0 — Finish First — User Review Later

Mặc định sản xuất V01 hoàn chỉnh, xác minh đầu ra dùng được và bàn giao trước khi người dùng đánh giá. Giữ 8 macro M0–M7, 99 ID packet, OpenFilm CLI-first, VieNeu-TTS GPU-first, ZIP ảnh và checkpoint.

- Một sự kiện phê duyệt phạm vi có thể bao phủ M1–M7; không cần QC_PASS, VISUAL_PASS, QC20 hoặc nghiệm thu từng macro để tiếp tục. Các quyền cài đặt/tải model/thay đổi hệ thống/CPU fallback/voice cloning/provider/phí/xóa/xuất bản vẫn riêng.
- Scheduler kiểm snapshot phạm vi, hash nguồn, đường dẫn trong workspace và đầu ra thực. Kiểm tra PNG/MP4 bằng giải mã; WAV/phụ đề/JSON/mã cảnh có kiểm tra kỹ thuật. OUTPUT_READY và DELIVERED_FOR_REVIEW tách khỏi USER_ACCEPTED.
- P18 là chẩn đoán tùy chọn; P20 là phản hồi sau bàn giao. P21 dùng lại V01 đúng định dạng. Revision tạo V02/V03, kiểm hash bản trước và giữ lịch sử.
- Migration sao lưu byte gốc trước atomic replace, chỉ chuyển trạng thái công việc khi có đầu ra; giữ dữ liệu, runtime, bằng chứng và approval cũ. Bundle cũ cần đối chiếu lại phạm vi; không tự cấp quyền mới. LEGACY_QC chỉ dùng để đọc/kiểm thử checkpoint cũ.
- QC nâng cao chuyển thành tùy chọn. Loại ví dụ dự án cụ thể khỏi ZIP handoff; giữ việc phân biệt ZIP trong chat và PNG đã nhập thật vào Windows.

## Bằng chứng kiểm thử ngày 20/11/2026

- Nguồn gốc: GitHub `main` tại `dcece398c834ae2b8fef954f5c472d54748e554c`, v1.13.0. 125 tệp văn bản từ Plugin Creator khớp nguồn này. Bản gốc đầy đủ đã sao lưu ZIP trước sửa; nhánh nâng cấp riêng `upgrade/v1.14.0-finish-first`.
- Baseline unittest: 116 bài, 3 lỗi môi trường (2 quyền symlink Windows, 1 encoding mặc định). Lần pytest baseline còn gặp lỗi thư mục tạm dùng chung. Các lần chạy sau dùng UTF-8 và thư mục tạm riêng.
- `python -X utf8 -m pytest -q --basetemp=.validation/pytest-final`: **223 passed, 2 skipped**. Hai bài symlink bỏ qua vì WinError 1314; không thay đổi quyền hệ thống. Các bài traversal và hash/scope chạy và đạt.
- ZIP handoff: 6 bài unittest riêng đạt; kiểm manifest, PNG, ZIP, hash và path.
- `scripts/run_windows_finish_first_fixture.py`: chạy OpenFilm CLI 0.4.0 có sẵn trên Windows, không cài/tải thêm. Scheduler lần lượt chọn bước đọc 7 nguồn → profile/FilmData → storyboard/PNG → WAV → phụ đề → cảnh → timeline → render V01 → DELIVERED_FOR_REVIEW. V01 và V02 đều được OpenFilm render thật, FFmpeg giải mã video/audio thành công, V01 giữ nguyên SHA256 sau V02.
- Chi tiết kích thước/hash/stream trong [bằng chứng thực thi](tests/evidence/finish-first-windows.json). Có checkpoint riêng sau từng đầu ra và sau bàn giao.

## Phạm vi đã kiểm chứng

Fixture dùng WAV tone tổng hợp, không phải giọng VieNeu. Sự kiện phê duyệt/phản hồi trong fixture là dữ liệu mô phỏng được đánh dấu rõ, không phải người dùng chấp nhận phim. Chưa kiểm inference VieNeu GPU hoặc thao tác nút của host trong phiên này. Bộ kiểm thử quyền GPU-first vẫn được giữ và chạy; không chuyển sang CPU. Không tuyên bố một phim thực tế với giọng đọc đã được nghiệm thu.

OpenFilm fixture được tạo trong thư mục kiểm thử mới; không sửa phim hay checkpoint của dự án cũ. Video kiểm thử không được tự xuất bản.

## Chạy lại

```powershell
python -X utf8 -m pytest -q --basetemp=.validation/pytest-recheck
python -X utf8 scripts/run_windows_finish_first_fixture.py --workspace .validation --cli ABSOLUTE_EXISTING_OPENFILM_CMD
```

Lệnh fixture cần runtime đã cài và workspace tồn tại. Không tự tải/cài nếu thiếu. Kiểm một file bằng `skills/openfilm-macro-bundles/references/finish_first.py --workspace WORKSPACE --path RELATIVE_FILE --require-audio` (chỉ bật require-audio khi cần stream âm thanh).

# Video-hoạt-hình v1.14.1 — sửa checkpoint và kiểm chứng sản xuất thật

Ngày kiểm thử: 20/11/2026 (Asia/Saigon). Giữ 33 kỹ năng, 8 macro M0–M7, 99 ID packet, OpenFilm CLI-first, VieNeu GPU-first và defaultPrompt. Không cài thêm phần mềm/model, không chuyển CPU, không sửa checkpoint dự án đang dùng.

| Hạng mục | Kết quả | Bằng chứng và giới hạn |
|---|---|---|
| T01 | PASS | ZIP v1.13.0 kiểm CRC và khôi phục 161 tệp vào thư mục mới; 133 tệp Git khớp commit dcece398. Đủ manifest 1.13.0 và 33 kỹ năng. Một entry manifest lặp có bytes giống hệt được ghi nhận. |
| T11 | PASS | Thiếu mode/phiên bản cũ không dispatch Finish First. Migration giữ backup, approval/path/hash/history và khóa quyền đến khi đối chiếu receipt cũ. Test v1.13 gồm resume cùng quyền. Copy checkpoint thật v1.11 được migration/restore; hash nguồn không đổi. |
| T12 | FAIL — chưa kiểm chứng UI native | Năm action backend được kiểm trên file thật và unit tests; một approval bao phủ nhiều macro. Host không cung cấp native callback/connected document executor để thử click thật. Không chế HOST_BUTTON hay acceptance. |
| T18 | PASS | VieNeu v3turbo model/codec local, PyTorch 2.8.0+cu128, RTX 4060; backbone và codec cuda:0. Ba WAV 48 kHz, 6.32/7.44/7.68 giây, ghép vào MP4. Mạng bị khóa, không CPU fallback. |
| T28 | PASS | So v1.13/v1.14 cho tám kỹ năng trọng tâm; phục hồi routing/trách nhiệm, production playbook, ZIP spec và host contract. Viết lại optional review để bỏ chỉ dẫn khóa phát hành legacy. |
| T30 | PASS | Lệnh yêu cầu: 244 passed, 0 failed, 2 skipped. Hai symlink tests thiếu Windows privilege; không thay cấu hình hệ thống. 33 YAML frontmatter hợp lệ, metadata/prompt/99 packet được đối chiếu. |
| T31 | PASS | Ba cảnh SVG/GSAP, bảy tệp kịch bản, FilmData, storyboard/assets, thoại GPU, VTT/SRT và chữ trong MP4. OpenFilm CLI 0.4.0 xuất 645 frame, 1280×720, 24 fps, 26.875 giây; MP4 có hình/tiếng và giải mã toàn bộ thành công. |
| T32 | PASS | Feedback mô phỏng đổi màu/hiệu ứng lan can S02. S01/S03, WAV và captions giữ nguyên hash. V02 render thực, V01 hash trước/sau giống nhau; không QC20, không lưu USER_ACCEPTED. |

Tổng: **7 PASS, 1 FAIL do UI native chưa kiểm chứng**. Đây không phải kết luận người dùng đã nghiệm thu toàn bộ gói.

## Bằng chứng

Gói riêng chứa `production/verified-run/V01.mp4`, `V02.mp4`, source hai phiên bản, WAV/captions, `GPU_EXECUTION.json`, log render, `EXECUTION_REPORT.json`, `DELIVERY_MANIFEST.json`, báo cáo restore/migration/docs, log pytest và lý do skip. Không đóng models/venv/cache. Nội dung checkpoint dự án cũ giữ cục bộ, không đưa lên GitHub/plugin.

- V01 SHA256: `9a8c95f7e503f69b52f7d16800159a8529e8b778d77093b01c9fa5c4a46db56e`.
- V02 SHA256: `1ad821ff7b9b6893628e7ec1234bae7f91dfce84302c4ed4f0e97a3d536731ac`.
- Backup v1.13.0 SHA256: `1f288c76b305a7f8023ae7231c7ac91316ca01c679b596d3b50ccbd8f3a4e5e0`.
- Git baseline v1.14.0: `1d653a111dad1ad04abe85f8c0abfa041df85297`; nhánh `upgrade/v1.14.0-finish-first` được giữ.

Commit bản sửa và Plugin Creator release ID được ghi trong biên nhận sau phát hành, tránh tự tham chiếu hash commit.

## Giới hạn

Native ChatGPT click chưa có đường kiểm chứng. Event backend replay được đánh dấu mô phỏng; ACCEPT_VIDEO chỉ kiểm trong bộ nhớ rồi bỏ, không lưu thành nghiệm thu phim thật. Scheduler được replay xuyên macro trên artifacts thật; không phải executor đã tự chạy toàn bộ các lệnh dựng nguồn ban đầu. Agent thực hiện sản xuất bằng runtime có sẵn.

Captions chia theo cụm từ dựa trên thời lượng WAV đo thật, chưa forced alignment cấp từ. Không có kết luận nghe/chấm phát âm hoặc thẩm mỹ thay người dùng. Frame mẫu chỉ chứng minh nội dung/caption xuất hiện, không chứng minh xem toàn phim.

Render V01 qua PowerShell trả mã shell 1 do stderr bị bọc NativeCommandError, dù OpenFilm báo hoàn tất 645 frame và file giải mã được. V02 dùng subprocess: exitCode=0, decodeExitCode=0. Log gốc giữ cục bộ; log bàn giao che khóa truy cập Studio. Không ghi giả exitCode V01.

Checkpoint thật đang có là v1.11.0; trường hợp v1.13.0 kiểm bằng regression fixtures. Migration copy giữ workspace/identity gốc và không thực thi dự án cũ. Thiếu receipt kiểm chứng được thì không tự khôi phục quyền từ planApprovalId.

## Tái lập

`python -X utf8 -m pytest -q --basetemp=.validation/pytest-recheck`

Scripts `run_vieneu_gpu.py`, `build_production_sample.py`, `render_sample_version.py`, `verify_production_delivery.py` dùng runtime đã cài và thư mục đầu ra mới. Đọc --help, cung cấp model/codec/GSAP/CLI thật; không tải phụ thuộc hoặc ghi đè media. `verify_backup_restore.py` khôi phục vào thư mục mới, kiểm CRC/bytes và Git base.

Vận hành chi tiết: `skills/openfilm-production-p06-p21/references/PRODUCTION_PLAYBOOK.md` và `skills/openfilm-macro-bundles/references/OPERATIONS.md`.

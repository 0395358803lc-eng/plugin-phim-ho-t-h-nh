# Finish First — v1.14.1

Thử migration trên bản sao: thêm `--copy-to NEW_FILE` trong thư mục đích đã chọn. Source checkpoint và workspace identity giữ nguyên; chỉ bản copy cùng backup được ghi. Đầu ra phải chưa tồn tại; hard link cùng thư mục công bố file hoàn chỉnh mà không ghi đè khi có concurrent writer. Bản copy vẫn cần scope revalidation trước execution.

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.

| Macro | Giai đoạn | Đầu ra và điều kiện tiếp tục |
|---|---|---|
| M0 | P00–P06 | Chọn máy/workspace, tái dùng runtime, phê duyệt thao tác đặc biệt. Fixture 7 giây chỉ dùng lần kiểm chứng runtime đầu hoặc chẩn đoán. |
| M1 | P07–P09 | Đọc đủ 7 tệp, chốt thông số trong phạm vi đã duyệt, tạo FilmData và film.html. |
| M2 | P10–P11 | Storyboard, nhân vật, bối cảnh, asset thật; ZIP và xác minh file sau giải nén. |
| M3 | P12–P13 | WAV VieNeu GPU, thời lượng thực, phụ đề. Bỏ qua có lý do nếu phim không có thoại. |
| M4 | P14–P16 | Mã cảnh 2D/3D theo FilmData, đủ tài sản và không còn placeholder cản render. |
| M5 | P17–P18 | Timeline hoàn chỉnh. P18 smoke chỉ khi chẩn đoán hoặc user yêu cầu. |
| M6 | P19–P20 | Render toàn phim thành V01.mp4, giải mã và kiểm stream. P20 chỉ kích hoạt sau phản hồi người dùng, không chặn P21. |
| M7 | P21 | Bàn giao trực tiếp V01 nếu đúng định dạng, source/WAV/phụ đề/manifest. Không render lại master trùng nội dung; không tự xuất bản. |

## Thực thi và checkpoint

1. Materialize packet từ FilmData, giữ ID template cũ; outputPaths phải là từng file cụ thể, không phải thư mục hay glob. Bỏ packet không cần bằng SKIPPED kèm skipReason.
2. `macro_scheduler.propose` tạo 8 nhóm logic; có thể trình các nhóm M1–M7 trong một `APPROVE_PRODUCTION`. Tách special risk thành nhóm riêng.
3. Event chứa deviceId, workspace, filmId, stateRevision, approvalId, source=USER_CHAT/HOST_BUTTON, at và snapshot chính xác từng bundle trong `bundles`. `validate_macro_event.validate` kiểm tra trước; `production_flow.apply_event` trả bản sao state, không tự ghi hoặc tự cấp quyền.
4. Mỗi bundle được duyệt lưu approvedScopeSha256. Đổi input, scope hoặc lệnh phải kiểm lại quyền. Input sinh bởi packet trước được kiểm theo output hash ngay trước bước dùng; không đòi hash file chưa tạo tại lúc duyệt.
5. Gọi `next_eligible_packet` trong từng lượt chat. Scheduler kiểm quyền, preflight, file phụ thuộc và hash thực. Sau chạy, dùng `finish_first.check_file` và lưu outputHashes trước OUTPUT_READY. Không dùng log thành công thay file.
6. Ghi checkpoint bằng temp file trong workspace rồi atomic replace; kiểm stateRevision/hash trước ghi, giữ bản cũ. Khi hết lượt, lưu nextPacketId và tiếp tục scope cũ trong lượt sau.
7. Khi video dùng được, ghi video.path, sha256, version, requiresAudio rồi DELIVER_VIDEO; gửi liên kết file thật. Không ghi USER_ACCEPTED từ kết quả giải mã.
8. Sau phản hồi, `revision_history.plan_revision` phân loại scene/audio/subtitle/effect và tạo đường dẫn V02/V03 chưa tồn tại. Chỉ sửa các targetIds liên quan; giữ videoHistory và hash V01. Render với quyền hiện hành; phát sinh lệnh/quyền mới cần phê duyệt riêng. `register_revision` kiểm cả phiên bản trước và đầu ra mới.

## Tương thích

`migrate_checkpoint.py CHECKPOINT --workspace WORKSPACE` sao lưu byte gốc trước khi thay checkpoint. QC_PASS/READY_FOR_REVIEW/PASS chỉ đổi OUTPUT_READY khi file tồn tại, dùng được và đúng hash; thiếu file đổi FAILED_TECHNICAL. BLOCKED kỹ thuật được giữ; VISUAL_BLOCKED đổi PLANNED để tiếp tục sản xuất, không tự hoàn thành. ID và dữ liệu cũ được giữ. Quyền cũ cần đối chiếu lại snapshot, không tự tạo approval. LEGACY_QC chỉ phục vụ đọc/kiểm thử checkpoint cũ, không chọn cho dự án mới.

QC nâng cao là công cụ tùy chọn khi user yêu cầu; các báo cáo không được thay trạng thái đầu ra. Bộ kiểm tra kỹ thuật không đánh giá thẩm mỹ.

## Migration an toàn v1.14.1

Thiếu productionMode là LEGACY_UNDECLARED kể cả khi pluginVersion ghi 1.14; explicit Finish First với pluginVersion trước 1.14 là LEGACY_VERSION. Không dispatch sang pipeline mới. Mode/schema/version không hỗ trợ bị từ chối; không suy ra ý định từ tên file.

`migrate_checkpoint.migrate(path, workspace)` lưu bản byte gốc .bak, flush/fsync, biến đổi trên deep copy và atomic replace sau khi kiểm source chưa đổi. Chỉ đổi các task rows; runtime/preflight/approval/event histories giữ nguyên. PLANNED/WAITING_APPROVAL/IN_PROGRESS/BLOCKED/INVALIDATED không tự thành OUTPUT_READY dù có file trùng tên. Trạng thái legacy từng báo hoàn thành chỉ được đổi khi file decode/path/hash hợp lệ.

Các trường quyền và bundle status cũ được giữ; thêm scopeRevalidationRequired để khóa execution sau migration. `restore_existing_approval(state, bundle_id, approval_id)` chỉ dùng receipt cũ có sẵn trong eventHistory/approvalHistory, đúng identity/snapshot/input hashes; không nhận một event mới để tự tạo quyền. Hàm trả copy và tăng revision. Caller vẫn phải xác minh receipt từ tương tác người dùng thật, rồi lưu atomic. Nếu thiếu receipt có thể kiểm chứng, ghi rõ giới hạn và chỉ làm rõ quyền một lần cho scope, không xin lại từng packet. Không sửa checkpoint dự án đang dùng để làm kiểm thử.

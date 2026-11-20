# `PRODUCTION_STATUS.json` — hợp đồng dữ liệu trạng thái

Vị trí: `VIDEO_HOAT_HINH_WORKSPACE/reports/PRODUCTION_STATUS.json`; không chứa token API, credentials, voice reference raw, dữ liệu nhận dạng nhạy cảm. Schema version `1`, chỉ điều phối 16 stage P06–P21, P00–P05 là gate môi trường độc lập.

Fields top-level:

- `schemaVersion`: `1`, `pluginVersion`: string, `deviceId`, `projectDir`, `workspace`, `filmId`, `sourceDir`, `sourceManifestPath`: null cho đến khi có máy/source thực. Không điền ví dụ như dữ liệu đã kiểm.
- `stages`: đủ P06..P21, mỗi stage có `id`, `name`, `status`, `planApproval`, `acceptanceApproval`, `qcStatus`, `evidence`, `workUnits`, `skipReason`.
- `planApproval` và `acceptanceApproval`: `{status: NOT_REQUESTED|PENDING|APPROVED|REJECTED, approvalId, scope, source, at}`. `APPROVED` phải có approvalId/scope/source/at; đừng tự suy ra `APPROVED` từ câu khen hoặc ID thiết bị.
- `workUnits[]`: `{unitId, status, sourceHashes:{}, outputs:[{path,sha256,kind}], qcEvidence:[], planApprovalId, updatedAt}`; `PASS` phải có bằng chứng và approved scope hợp lệ.
- `evidence[]`: đường dẫn thực đến báo cáo/screenshot/log/metadata có thể truy cập; không dùng placeholder trong hồ sơ PASS.

Tính đúng đắn tối thiểu:

1. Danh sách stage có chính xác P06–P21, đúng thứ tự, không trùng; status thuộc enum.
2. PASS ⇒ planApproval APPROVED (trừ stage read-only P07 nếu chỉ audit), acceptanceApproval APPROVED, qcStatus PASS, evidence không rỗng. Khi unit bắt buộc còn FAIL/BLOCKED/NOT_STARTED ⇒ stage không PASS.
3. SKIPPED ⇒ `skipReason` có thật, evidence, acceptanceApproval APPROVED; chỉ cho phép P06/P12/P13/P14/P15 khi scope không yêu cầu hạng mục (P13 có thể skip nếu không có cả thoại và phụ đề theo brief).
4. PASS hoặc SKIPPED của stage sau không được đứng trước stage trước chưa PASS/SKIPPED, trừ khi người dùng cho phép ngoại lệ được ghi rõ; mặc định validator báo lỗi.
5. Source hash thay đổi ⇒ invalidation liên quan; `PAST PASS` không tự trở thành PASS trong phiên mới nếu file thay đổi; validator JSON không thay thế kiểm tra hash file thực.
6. P21 PASS ⇒ artifact `FINAL_MASTER.mp4` thật cùng ffprobe/playback evidence, P20 PASS. Nếu chỉ có JSON/template thì P21 NOT_STARTED.

Ví dụ phê duyệt từ chat (đây chỉ là chuỗi văn bản, không phải một host callback đã triển khai): `Tôi PHÊ DUYỆT THỰC HIỆN P12 với dialogue_id D001–D005, sử dụng preset voice, tạo WAV vào <workspace>/projects/<film-id>/assets/audio/voice; không voice cloning.`

Sổ log approval JSONL append-only với `decisionId`, `phaseId`, `unitId`, `decision`, `scope`, `source=chat|host`, `time`, `evidenceRef`, `status=verified|unverified`. Không tự tạo lời phê duyệt của người dùng. 

**Kiểm tra tệp có thật:** chạy `python validate_production_state.py reports/PRODUCTION_STATUS.json --check-files <WORKSPACE>` sau khi được quyền đọc workspace. Lệnh chỉ đọc kiểm tra evidence/output file tồn tại, không rỗng, hash đã khai báo và path không trỏ ra ngoài workspace; với P21 kiểm tra có `renders/master/FINAL_MASTER.mp4`. Việc này **không thay thế** bước xem/nghe MP4, kiểm FFprobe, QC20 và phê duyệt của người dùng.

## Extension v1.6.0 — work packets

Giữ nguyên schemaVersion=1 của `PRODUCTION_STATUS.json` và validator cũ. Bổ sung file index **tùy chọn** `reports/WORK_UNIT_INDEX.json` (`schemaVersion=1`, `pluginVersion=1.6.0`, `stateRevision` tăng sau mỗi commit atomic, `packets[]`, `currentPacketId`, `nextPacketId`); tránh phá dữ liệu cũ và không lạm dụng JSON này để tự xác nhận người dùng. Ví dụ cấu trúc trong `openfilm-high-workpackets/references/WORK_UNIT_INDEX_TEMPLATE.json`.

Trạng thái gói: `PLANNED`, `WAITING_APPROVAL`, `IN_PROGRESS`, `READY_FOR_REVIEW`, `PASS`, `FAIL`, `BLOCKED`, `INVALIDATED`, `SKIPPED`. `qcStatus` riêng `NOT_TESTED|PASS|FAIL|BLOCKED|NOT_APPLICABLE`. `PASS` chỉ khi có explicit user acceptance và evidence/file; có file QC PASS nhưng chưa bấm phải `READY_FOR_REVIEW`. Dự án quay lại phiên cũ phải đọc index + state và xác minh hashes/record thật, không tăng revision giả. Khi index conflict với state cũ, BLOCKED và trình reconcile có review, không tự ghi đè.

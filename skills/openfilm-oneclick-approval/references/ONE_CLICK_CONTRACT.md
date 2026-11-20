# Hợp đồng thao tác host — v1.14.1

Chỉ dùng API/nút tương tác thật mà host hiện cung cấp. Plugin kỹ năng không tự đăng ký callback hoặc biến Markdown thành nút. Không giả định GenUI.issueNewTurn tồn tại. Nếu host không có UI thao tác, dùng câu trả lời trong chat và liên kết file thật; ghi host UI là NOT_VERIFIED, không tạo HOST_BUTTON receipt.

| Nhãn | Action | Hiệu lực |
|---|---|---|
| Tiếp tục sản xuất V01 | RESUME_APPROVED_MACRO | Dùng quyền scope hiện có; không duyệt lại |
| Xem tiến độ | VIEW_PROGRESS | Chỉ đọc packet/stage/video hiện tại |
| Xem video V01 | VIEW_VIDEO | Chỉ đọc video đúng path/hash/version |
| Chấp nhận video | ACCEPT_VIDEO | Chỉ sau DELIVERED_FOR_REVIEW và phản hồi thật |
| Yêu cầu chỉnh sửa | REQUEST_REVISION | Cần feedback category/targetIds/request |
| Duyệt phạm vi sản xuất, khi chưa có quyền | APPROVE_PRODUCTION | Một event bao phủ nhiều macro đã trình |

Mỗi event gắn stateRevision, deviceId, workspace, filmId hiện hành. Event đổi trạng thái phải dùng snapshot scope của bundle (macroId/macroIds/stageIds/packetIds/scopeIds/allowedPaths/allowedCommands/riskClass/inputHashes/specialApprovalRequired). APPROVE_PRODUCTION có macroBundleIds và bundles theo ID. Một lần user cấp phạm vi có thể bao phủ M1–M7; không phát sinh nút từng packet.

Đối chiếu tương tác thật trước khi gọi validator. Các chuỗi source=USER_CHAT/HOST_BUTTON và approvalId trong JSON không tự chứng minh người dùng đã click. Không nhận một file event do model sinh làm quyền. Test fixtures gắn simulated/testOnly và không được lưu vào checkpoint production như acceptance thật.

Đọc lại checkpoint trước mỗi callback. `validate_approval_event.validate` kiểm identity/revision và chuyển event có quyền sang production_flow. Xem chỉ trả dữ liệu/link, không append approval hoặc tăng revision. Apply_event trả copy; caller ghi atomic với đối chiếu revision/hash và giữ bản cũ. Callback stale bị từ chối, không tự retry dưới quyền mới.

RESUME chỉ cho bundle APPROVED/IN_PROGRESS với seal scope còn đúng; scheduler tự qua macro tiếp theo đã được duyệt. Nếu không còn packet, trả tiến độ/bàn giao. ACCEPT_VIDEO chỉ cho video đã giao; REQUEST_REVISION cần feedback và không đổi thành USER_ACCEPTED. Không thử ACCEPT_VIDEO trên dự án thật chỉ để chứng minh nút hoạt động.

Hợp đồng packet/bundle v1.6–v1.10 chỉ còn trong validator LEGACY_QC để đọc hồ sơ cũ; không trình UI theo hợp đồng đó cho dự án mới. Checkpoint thiếu productionMode phải migration trước mọi action production.

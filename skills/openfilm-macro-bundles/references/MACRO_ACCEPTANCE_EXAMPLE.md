# Ví dụ hợp đồng một macro (chỉ minh họa, KHÔNG phải sự kiện duyệt thật)

Khi người dùng đã chọn đúng Windows device, WORKSPACE và scope được công bố:

```json
{
  "macroBundleId": "M5.B001",
  "macroId": "M5",
  "stageIds": ["P17", "P18"],
  "packetIds": ["P17.01.FILM001", "P18.02.SMOKE001"],
  "scopeIds": ["FILM001", "SMOKE001"],
  "allowedPaths": ["projects/film001/openfilm/film.html", "renders/smoke/smoke-5s.mp4"],
  "allowedCommands": ["openfilm render 0-5 --out renders/smoke/smoke-5s.mp4"],
  "riskClass": "NORMAL",
  "status": "PLANNED",
  "presentedToUserRevision": 42,
  "planApprovalId": null,
  "inputHashes": {"projects/film001/openfilm/film.html": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
  "evidencePaths": []
}
```

**Đây chỉ là mô phỏng.** Không tái sử dụng hash, ID, cmdline, path hoặc version mà chưa đọc file/thư mục máy thật. `APPROVE_MACRO` chỉ từ user action; một lần duyệt cho M5 bao phủ P17+P18 nếu đã công bố đầy đủ scope. Không được tự tạo lượt mới khi chưa có click. P17 và P18 vẫn QC riêng.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate

Ví dụ v1.12 M6/M7: kiểm tra `visualTargets`, `visualGates[macroId]` với `{status:"VISUAL_PASS",reportPath:"qc/visual/M6/VISUAL_QC_REPORT.json",reportSha256:"<SHA256 verified>",stateRevision:current}`, chỉ sau **khi thực sự thấy ảnh trong ChatGPT**. Nút nghiệm thu gửi `visualReportSha256` trùng report đã xem; tuyệt đối không dùng hash mẫu hoặc chuỗi placeholder trong nút thật. Report M6 phải tham chiếu draft MP4; report M7 tham chiếu final MP4 mới, không dùng hình M6 thay M7.

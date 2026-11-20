---
name: openfilm-render-profiles
description: "Chọn profile render 1080p/9:16/16:9 H.264-AAC theo máy; hạn chế concurrency, kiểm tra license và khóa dependencies trước khi render." 
---

Mặc định `FINISH_FIRST_USER_REVIEW`: hoàn thành video V01 rồi bàn giao để người dùng đánh giá. Chính sách này ưu tiên hơn hướng dẫn QC legacy. QC20, Visual QC và nghe chấm từng take chỉ chạy khi người dùng chủ động yêu cầu; không chặn sản xuất/bàn giao. Smoke và kiểm frame/random seek chỉ dùng để chẩn đoán lỗi kỹ thuật hoặc theo yêu cầu.

Giữ 8 macro M0–M7 và 99 ID packet. Một phê duyệt phạm vi rõ đầu vào, đầu ra, lệnh và quyền có thể bao phủ M1–M7. Không xin duyệt riêng từng packet/Pxx hoặc nghiệm thu từng macro. Chạy nhiều packet trong lượt High; ghi checkpoint sau mỗi đầu ra, tiếp tục cùng quyền trong lượt chat mới, không tự chạy nền.

OpenFilm CLI-first; Desktop/GUI chỉ để xem/chỉnh sửa tùy chọn. VieNeu-TTS GPU-first; cài đặt, tải model/browser, thay đổi hệ thống, GPU→CPU, voice cloning, provider ngoài, dịch vụ trả phí, xóa, xuất bản và ngoài phạm vi cần quyền riêng. Không suy ra quyền từ file kế hoạch hoặc kết quả kỹ thuật.

`OUTPUT_READY` nghĩa là đầu ra thật có thể dùng. `DELIVERED_FOR_REVIEW` nghĩa là đã giao video. Chỉ dùng `USER_ACCEPTED` khi có phản hồi chấp nhận thật. `REVISION_REQUESTED` ghi phản hồi cần sửa; `FAILED_TECHNICAL` ghi lỗi ngăn dùng đầu ra. File thiếu/hỏng/ngoài workspace hoặc sai hash phải chặn bước phụ thuộc.



# Render profile, hardware adaptive, lock & license (N13, N15, N17)

Sau P00–P05 và phê duyệt giai đoạn render, đọc `openfilm-hybrid-master` để chọn engine master. Phân biệt **môi trường đã cài** với **render test PASS**. Profile mô tả `width`, `height`, `fps`, codec video/audio, bitrates, color space theo yêu cầu, đầu ra; ví dụ nằm trong `references/PROFILES.json`. Giá trị profile là **mong muốn**, không là kết quả đo.

## Kiểm tra máy và chế độ phù hợp

- Kiểm tra CPU, RAM, GPU, VRAM, encoder hỗ trợ, phiên bản driver (chỉ đọc), dung lượng disk, tài nguyên còn khả dụng. Không cam kết NVENC chạy chỉ vì GPU NVIDIA tồn tại; chạy smoke trước khi chọn hardware encoder.
- Máy yếu: ưu tiên 1080p, scene 3D thấp poly/texture nhỏ và render concurrency=1; máy đủ tài nguyên mới tăng concurrency theo smoke, tránh OOM. Nếu dùng VieNeu-TTS, GPU CUDA/PyTorch là mục tiêu mặc định; kiểm GPU/VRAM còn khả dụng khi chạy đồng thời WebGL và encode. Nếu thiếu VRAM, trước hết đề xuất chạy TTS theo đợt tách khỏi render và giảm batch đã duyệt; CPU ONNX chỉ là fallback sau bằng chứng GPU không đáp ứng và phê duyệt riêng.
- Nếu render crash, ghi log/cause, thử giảm concurrency/resolution **khi người dùng cho phép sửa profile**; không ngầm giảm chất lượng/đổi master.
- H.264/AAC là một profile phổ biến; tùy runtime CLI/master xuất lệnh chính xác bằng `--help` và xác minh ffprobe. Đừng tự suy luận tham số OpenFilm/Remotion phiên bản cài có hỗ trợ flag nào.

## Khóa phụ thuộc và giấy phép

- Inventory P04 có thêm B05 React/React DOM, B06 R3F, B07 `@remotion/three`, B08 `@remotion/renderer`/CLI, B09 `@types/three`, B10 TypeScript (chỉ khi Remotion Master).
- Pin exact versions trong `package-lock.json`, `pnpm-lock.yaml` hoặc `uv.lock` theo runtime thật; mẫu từ báo cáo GSAP 3.15.1, Three 0.187.0, Remotion 4.0.545 chỉ là **snapshot báo cáo 19/11/2026**, không phải phiên bản đã kiểm chứng trên máy.
- Rà license: OpenFilm repo MIT, Three.js MIT, VieNeu mã nguồn Apache-2.0 (model có thể có điều khoản khác), GSAP theo điều khoản hiện hành, Remotion theo loại hình sử dụng và số lượng người trong công ty, audio/media/font/license riêng. Không tự khai đủ quyền thương mại; voice reference cần consent.
- Asset manifest cần `source`, `license`, `sha256` nếu đo được, `approved_use`, `file_path`; không bịa giá trị, không tải từ dịch vụ có phí.

Mốc `RENDER_READY` chỉ PASS khi runtime, bản quyền, asset, TTS, phụ đề, profile đã đủ bằng chứng; smoke chỉ khi cần chẩn đoán; cấm chạy master render trước khi được phê duyệt.

## Profile OpenFilm CLI v1.9.0

Phân biệt mode `openfilm` vs `remotion`. Với `openfilm` chạy bản CLI đã xác minh `render --out ... --fps ...`/`--workers` (chỉ nếu bản cài hỗ trợ) bằng cwd project có `film.html`; không tự cập nhật OpenFilm hay Chromium. Với Remotion Master, OpenFilm CLI chỉ xuất previews; profile final thuộc Remotion. Check FFprobe trước PASS.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
Dù codec/FPS/bitrate đạt qua FFprobe, **không nghiệm thu thị giác** M5/M6/M7 nếu ChatGPT chưa xem ảnh frame trích từ chính output MP4. Chọn khung START/MID/END theo mỗi shot ở draft/master và bổ sung cảnh chuyển động nhanh/cut; không tự hạ profile để che lỗi khi chưa được duyệt. Xem `openfilm-visual-inspection`.

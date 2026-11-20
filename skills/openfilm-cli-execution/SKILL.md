---
name: openfilm-cli-execution
description: "Bắt buộc dùng OpenFilm CLI làm đường điều khiển của Video-hoạt-hình từ P04–P21 trên Windows; xác minh binary, cwd, lệnh open/look/render/canvas, kết quả, log, phê duyệt và không tải ngầm."
---

# OpenFilm CLI-first (v1.9.0)

**CLI_ONLY_FOR_OPENFILM:** OpenFilm CLI là **đường điều khiển chính và bắt buộc** cho tất cả gói có OpenFilm trong P06–P21, bất kể `OpenFilm Master` hay `Remotion Master` (vì Remotion Master vẫn cần OpenFilm CLI cho previs nếu previs là một phần quy trình). OpenFilm Desktop **không thay thế CLI**, chỉ là giao diện xem/chỉnh sửa tùy chọn được mở qua `openfilm open` khi user duyệt. Không tìm CLI được -> `BLOCKED`, trình A02 cài/tái dùng, không chuyển UI-only hoặc Remotion để tự bỏ qua quy tắc này. Riêng câu hỏi lý thuyết không cần runtime.

## P00–P06: audit, reuse, approval

- P00 kết nối Windows được chọn → P01 thư mục → P02 `VIDEO_HOAT_HINH_WORKSPACE` → P03 tìm CLI hợp lệ tại **workspace cũ được phép**, workspace hiện tại và hệ thống → P04 read-only A02 CLI (bắt buộc), A03 Node.js **>=22.2** (CLI npm), A04 FFmpeg/FFprobe, A05 Chromium/headless phù hợp (lần đầu có thể tải browser), A01 Desktop `TÙY CHỌN`, A06 Studio/browser `TÙY CHỌN` → P05 bảng phê duyệt ID còn thiếu và download budget. App Desktop chỉ được reuse làm nguồn CLI nếu có **CLI entrypoint thực được chứng minh**, không lấy tên ứng dụng làm bằng chứng.
- Ở P03/P04 không dùng `npx`, `npm install`, `openfilm doctor`, `openfilm open`, `openfilm look`, `openfilm render` hay lệnh nào có thể tạo cache/tải browser; chỉ đọc `Get-Command`, `package.json`, `node_modules/.bin/openfilm.cmd`, metadata phiên bản, file hash, PATH và runtime thư mục đã duyệt. `npx openfilm` hoặc `npx -y openfilm@latest` không được tự gọi khi chưa phê duyệt vì có thể tải package; ưu tiên **lệnh local đã xác minh** (Windows `openfilm.cmd` hoặc `.exe` nếu nhà phát hành thực sự cung cấp). Không cài global mặc định, không tự `corepack` hoặc tải Chromium.
- P06 sau phê duyệt tách **bootstrap CLI** (cài nếu thiếu đúng ID/phiên bản, checksum/scope), **command capability** (`--help`, `open`, `look`, `render` trong môi trường có quyền), và **smoke 7 giây**. Khả năng `render` chưa chứng minh ở máy mới: chỉ lần thử P06.10 được phê duyệt mới tạo chứng cứ; P06.11 FFprobe/xem-nghe xác minh rồi mới `READY_FOR_RENDER`. CLI có lệnh chưa đồng nghĩa runtime đủ FFmpeg/browser. `OPENFILM_RUNTIME_PROFILE.json` phải có mode `cli`, executablePath tuyệt đối, workingDirectory trong workspace, Node/version, log và bằng chứng; `mode=desktop-ui` không đủ điều kiện sản xuất.

## Lệnh OpenFilm CLI đã được tài liệu công bố

Lệnh cụ thể và cờ luôn phải được đối chiếu **`openfilm <command> --help` của bản đã cài** trong P06, không dùng option không được bản đó hỗ trợ. Thực thi từng lệnh từ **thư mục chứa `film.html`** (project OpenFilm hoặc fixture E2E). Phải có `deviceId`, workspace, cwd, exe absolute, phiên bản, args, expected outputs, approval ID và packet ID trước khi gọi.

| Công đoạn | Lệnh qua binary đã xác minh | Kết quả và kiểm tra |
|---|---|---|
| P06 probe | `openfilm --help` / `openfilm <command> --help` | Lưu stdout, exitCode, phiên bản; không suy luận render PASS |
| P09 scaffold | Tạo `film.html` qua script offline được duyệt | **Không cần** `openfilm open`; không tự tạo project nơi khác |
| P10 Canvas (tùy chọn) | `openfilm canvas` / `openfilm canvas apply` | Board thật; `apply` cần approval riêng; không gọi provider tạo media/TTS |
| P14–P16 kiểm hình | `openfilm look [what] [t|a-b]` | PNG/cache/log từ bản chạy thật; kiểm deterministic, lỗi cảnh |
| P16 Studio (tùy chọn) | `openfilm open [folder]` | Có thể bật Studio và download browser lần đầu; phải xin quyền trước; UI không phải renderer thay thế |
| P18 smoke | `openfilm render [a-b] --out <file>` nếu `--help` hỗ trợ | 5s đúng range; MP4 thật, stdout/stderr, exitCode, FFprobe |
| P19 draft | `openfilm render --out <file>` | File draft đúng nơi được duyệt, không ghi đè bản duyệt |
| P20 QC | `openfilm look [t|a-b]`, check FFprobe | Sửa một cảnh lỗi đã duyệt rồi nhìn lại |
| P21 master | `openfilm render --out <file> --fps <fps> [--workers <n>]` chỉ theo `--help` | MP4 thật, streams, frame/FPS, video+audio/credit review, QC20 |

**PowerShell nguyên tắc (minh họa, KHÔNG chạy nguyên văn):** đặt `$cli='D:\...\openfilm.cmd'`; `$filmDir='D:\...\projects\film-001\openfilm'`; `Push-Location -LiteralPath $filmDir`; `try { & $cli look '0'; $exit=$LASTEXITCODE } finally { Pop-Location }`. Đường dẫn lấy từ hồ sơ và kiểm reparse point; arg phải là danh sách rõ ràng, không nối chuỗi bằng `Invoke-Expression`, `cmd /c` hay `npx @latest`; không chèn giá trị nguồn chưa tin vào shell script. Trên máy Windows có thể bị execution policy/ACL hạn chế; báo `BLOCKED`, không sửa policy hệ thống.

**Exit codes theo tài liệu CLI:** `0` hoàn tất, `1` lỗi film/lệnh, `2` sai lệnh hoặc ngoài project; tuy nhiên phải lưu exitCode, stderr và xác minh **artifact thực**. `openfilm look` tạo PNG dưới `.film/cache/look`; `render` theo tài liệu mặc định viết MP4 cạnh `film.html`, `render [a-b]` vào `.film/cache/render`; luôn ưu tiên `--out` khi bản cài hỗ trợ và đích đã được duyệt. Không suy ra đường dẫn output từ docs nếu file thực khác. CLI `open` có thể tạo `film.html` hoặc mở Studio, không dùng để khởi tạo khi P09 đã có bootstrap riêng.

`references/CLI_COMMAND_CONTRACT.md` chứa command-safe gates; `references/CLI_RUN_TEMPLATE.json` và `validate_cli_run.py` là kiểm tra tĩnh record lệnh (không gọi CLI, không chứng minh file thực). Mỗi packet OpenFilm lưu record có `workingDirectory` (`cwd`), lệnh, args, log, file bằng chứng, exit code, stdout/stderr nếu có; xem lại evidence thực rồi mới QC PASS. Thời gian/ảnh/âm thanh cần review thực. Một packet/lượt High, các nút approval P06–P21 cũ không đổi.

## Hai chế độ master

- **OpenFilm Master**: OpenFilm CLI làm dự án, `look` kiểm ảnh, `render` xuất draft/master. Studio chỉ để người xem tùy chọn.
- **Remotion Master**: OpenFilm CLI làm dự án previs/`look` và **render previs MP4 khi được duyệt**, sau đó bàn giao file/FilmData cho Remotion CLI kết xuất cuối. Không gọi render cuối OpenFilm trong Remotion Master; OpenFilm Desktop không bắt buộc. Không chuyển `film.html` sang JSX bằng API giả định.

**Tuyệt đối không** biến việc nâng cấp skill v1.9 thành quyền cài/ghi/render trên PC. Cần quyền P05/P06 cho cài đặt/thử nghiệm đặc biệt và quyền macro M0–M7 có scope rõ cho các lệnh CLI thường. Một lệnh `look`/`probe` nội bộ không phát sinh nút duyệt riêng. Đọc `openfilm-macro-bundles/SKILL.md` v1.11.0 (các chỉ dẫn packet-level trước đây là LEGACY). Chưa thử thực tế trên Windows: trạng thái `NOT_TESTED`, không khẳng định OpenFilm CLI đã chạy.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
Kết quả OpenFilm CLI `look`/`render` chỉ chứng minh lệnh được chạy; M4 cần `read_file`/`read_multiple_files` ảnh screenshot thực và ChatGPT quan sát. M5/M6/M7 phải FFmpeg trích frame từ MP4 xuất thật, sau đó **ChatGPT nhìn các frame**, so storyboard/thiết kế. `visualGates` chặn macro accept nếu chỉ log hoặc không có multimodal image. Không mở GUI Desktop thay OpenFilm CLI; giữ scope/pin/approval hiện hành.

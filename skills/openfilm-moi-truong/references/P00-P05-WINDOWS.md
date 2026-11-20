# VIDEO_HOAT_HINH_WORKSPACE · Windows P00–P05 checklist (v1.4.0)

## Phạm vi

Áp dụng trên máy Windows đã được người dùng chọn qua Remote Desktop Commander được kết nối riêng. Đây là **quy trình hướng dẫn**, không phải bằng chứng máy đã được kết nối hoặc cài đặt. P00–P01: kiểm tra không ghi; **P02**: được tạo workspace trong thư mục dự án người dùng vừa chọn; P03–P05: chỉ đọc, không cài/ tải/ render.

## Sơ đồ trạng thái

`P00 CONNECTED` → `P01 PATH_SELECTED` → `P02 WORKSPACE_CREATED_OR_REUSED` → `P03 OLD_WORKSPACE_DISCOVERY` → `P04 SOFTWARE_AUDIT` → `P05 APPROVAL_REPORT` → `STOP`. Nếu BLOCKED ở bất kỳ cổng nào, không nhảy qua cổng. Không kiểm tra software ở P00–P02, ngoài kiến trúc OS và kiểm tra an toàn đường dẫn.

### P00: Xác định máy

Dùng danh sách deviceId thực tế; hỏi máy nếu chưa có lựa chọn; xác minh hostname/deviceId/Windows và quyền Remote Desktop Commander. Không được lấy máy từ ghi nhớ. Nếu công cụ không sẵn, mô tả hướng dẫn thủ công, không khẳng định có kết nối.

### P01: Người dùng chọn thư mục gốc dự án

Prompt một câu sau khi kết nối: `Bạn chọn thư mục dự án nào trên [hostname]? Ví dụ D:\Videos\DuAn01.` Nếu đã có đường dẫn từ yêu cầu hiện hành, không hỏi lại. Chuẩn hóa path Windows, bỏ dấu gạch cuối, không chọn nhầm file/ổ khác; nếu basename chính xác `VIDEO_HOAT_HINH_WORKSPACE`, không nối thêm lần nữa. Chỉ xác minh parent/path hợp lệ, quyền và reparse point trước khi tạo.

### P02: Tạo/xác minh workspace rồi mới kiểm tra phần mềm

Dự kiến:

```text
<PROJECT_DIR>\VIDEO_HOAT_HINH_WORKSPACE\
  tools\            # công cụ bổ sung cục bộ (sau phê duyệt)
  cache\            # caches cục bộ, chỉ khi được phép
  projects\         # các phim/sản phẩm
  assets\           # ảnh/âm thanh/đồ họa đầu vào
  renders\          # clip trung gian và MP4
  qc\               # kết quả nghiệm thu
  logs\             # log
  reports\          # báo cáo trạng thái
```

Đây là ví dụ cấu trúc **không chứa công cụ đã cài**, không coi folder trống là đã có phần mềm. Khi chọn thư mục root workspace sẵn thì dùng trực tiếp. Trước khi tạo, kiểm tra root không phải reparse point/link chuyển hướng ngoài quyền; thư mục đã tồn tại thì không ghi đè/xóa; nếu cần tạo chỉ tạo trong vùng path cho phép. Dùng thao tác tạo thư mục có kiểm tra tồn tại (idempotent), báo `CREATED` hoặc `EXISTING`; xác minh sau thực thi bằng truy vấn lại. Không chạm project khác. Không chạy `npm init`, `npm install`, `npx` ở P02.

### P03: Kiểm tra workspace dự án trước để tái sử dụng

Thư mục hiện tại tạo ở P02 **không** được coi là "workspace cũ". Vùng tìm kiếm: đường dẫn workspace cũ do người dùng cung cấp; đường dẫn dự án anh em và root người dùng cho phép, scan có giới hạn (không full-disk, không recursive vô hạn). Trạng thái:

| Mã | Điều kiện | Xử lý |
| --- | --- | --- |
| REUSE_OK | File hợp lệ, xác minh nguồn + version + chức năng + kiến trúc + quyền; đường dẫn gốc vẫn truy cập được | Tham chiếu trực tiếp, không cài lại |
| REUSE_PARTIAL | Có file nhưng chỉ một phần phụ thuộc, hoặc path/Node ABI không tương thích | Không tuyên bố tái sử dụng toàn phần, trình xử lý |
| REUSE_UNVERIFIED | Chưa đủ bằng chứng hoặc bản không rõ nguồn | Chưa chạy binary, đánh dấu cần kiểm chứng |
| REUSE_NONE_IN_SCOPE | Không thấy workspace cũ trong vùng được phép | Tiếp tục P04, không mặc nhiên liệt kê tất cả là thiếu |

Dò metadata như `tools`, `package.json`, lockfiles, manifests runtime, các .venv Python, package `vieneu`, cache model/ONNX và đường dẫn `node_modules`; không duyệt hoặc tải nội dung secrets. Cấm tự copy/move/link, sửa global PATH/registry, chạy các scripts install, quyền ACL, driver/OS; các package Node cần đánh giá khả năng resolve từ dự án mới trước khi dùng, không giả định có file = chạy được.

### P04: Kiểm kê 9 thành phần nền tảng + B04 VieNeu-TTS và T01–T07 (read-only)

| ID | Thành phần | Cách kiểm chứng và điều kiện cần |
| --- | --- | --- |
| A01 | OpenFilm Desktop | ứng dụng và version; bản packaged có thể đã đủ render |
| A02 | OpenFilm CLI | path/package version, chỉ cần nếu dùng CLI |
| A03 | Node.js/npm | `Get-Command`, version; CLI ≥22.2, source ≥22.18; Remotion chỉ khi bật |
| A04 | FFmpeg/FFprobe | bản app-bundled, bản hệ thống hoặc workspace cũ, version và mode |
| A05 | Chromium/Playwright | bản được OpenFilm/Remotion hỗ trợ; không ngầm download |
| A06 | Chrome/Edge | chỉ để Studio trên trình duyệt ngoài nếu cần |
| B01 | GSAP | version trong app/project/import map/vendor/lockfile, chức năng seek timeline; chỉ cần khi dùng GSAP |
| B02 | Three.js | version/module resolution + WebGL support; chỉ cần khi cảnh 3D |
| B03 | Remotion | React, `remotion`, `@remotion/renderer`/CLI và Node/runtime tương thích; chỉ cần template React hoặc batch |
| B04 | VieNeu-TTS | Khi cần giọng đọc tiếng Việt: SDK, môi trường Python, model/cache và thử nghiệm (chỉ sau duyệt); không đồng nhất metadata với runtime hoạt động |
| T01 | Python >=3.10 theo pyproject upstream | Phát hiện binary/path/architecture, venv trong workspace cũ hoặc Python phù hợp; không mặc định cài global |
| T02 | uv / trình quản lý môi trường | Tùy theo đường triển khai đã duyệt và khả năng tái dùng .venv |
| T03 | SDK `vieneu`, các package phụ thuộc | Dist-info, lockfile, version; kiểm path GPU venv, không khởi tạo SDK trong kiểm kê |
| T04 | Model VieNeu-TTS v3 Turbo / cache local | Dò cache được phép và model revision/manifest/license, không tự tải checkpoint hay gửi danh tính người dùng |
| T05 | PyTorch CUDA + torchaudio + transformers | **Cần cho VieNeu-TTS GPU-first** khi có NVIDIA GPU tương thích; pin bản theo wheel/Python/driver, không sửa driver/CUDA toolkit |
| T06 | NVIDIA GPU, VRAM, driver và điều kiện CUDA | Kiểm read-only bằng thông tin hệ thống/`nvidia-smi` nếu có, không khẳng định GPU ready chỉ vì nhận diện tên GPU |
| T07 | CPU/ONNX dự phòng | Chỉ đề xuất nếu GPU được chứng minh không đáp ứng; yêu cầu phê duyệt CPU fallback riêng, không tự cài |

Cùng một ID có thể có nhiều nguồn; ghi rõ ưu tiên app-bundled → workspace cũ hợp lệ → bản hệ thống đã có → kế hoạch cài cục bộ. `node_modules` không portable đương nhiên; chỉ xác minh bằng bằng chứng phù hợp. Ưu tiên package local, không cài global mặc định. Các lệnh dò đọc: `Get-Command`, `Get-Item`, `Get-ItemProperty`, `Get-ChildItem` giới hạn path/độ sâu, đọc JSON/lock, metadata file. Tránh `npx` vì có thể tải tự động, tránh `npm install`, `pnpm install`, `playwright install`, các installer và browser launch gây cache trong P04. Nếu một "doctor" không bảo đảm read-only thì không chạy.

### P05: Báo cáo bắt buộc và mẫu duyệt

Thiết bị: `[hostname]` / `[deviceId]` · Dự án: `[PROJECT_DIR]` · Workspace: `[WORKSPACE]` · Workspace trạng thái `[CREATED|EXISTING|BLOCKED]` · Roots cũ đã duyệt `[paths]` · Chế độ `[Desktop|CLI|source]` · Features `[GSAP/Three/Remotion/VieNeu-TTS]`.

| ID | Thành phần | Hiện trạng | Phiên bản | Đường dẫn nguồn + bằng chứng | Hành động |
| --- | --- | --- | --- | --- | --- |
| A01–A06 | OpenFilm + runtime | ... | ... | ... | Dùng lại / điều tra / thiếu |
| B01 | GSAP | ... | ... | ... | Dùng lại / tùy chọn / thiếu |
| B02 | Three.js | ... | ... | ... | Dùng lại / tùy chọn / thiếu |
| B03 | Remotion | ... | ... | ... | Dùng lại / tùy chọn / thiếu |
| B04 | VieNeu-TTS | ... | ... | ... | Tạo thuyết minh/thoại (khi cần) |
| T01–T07 | Python, uv, SDK, model cache, GPU CUDA ưu tiên và CPU fallback có điều kiện | ... | ... | ... | GPU-first / Reuse / CPU-chờ-duyệt |

Trạng thái hỗ trợ: `ĐÃ CÓ–TÁI SỬ DỤNG`, `CÓ SẴN TRONG APP`, `THIẾU CẦN CÀI`, `KHÔNG TƯƠNG THÍCH`, `LỖI`, `CHƯA XÁC MINH`, `KHÔNG CẦN`, `TÙY CHỌN CHƯA KÍCH HOẠT`. Chỉ gọi thiếu khi đã kiểm tra mode/đường dẫn được phép. Nếu không tìm thấy workspace cũ, nêu cụ thể phạm vi đã rà và phần chưa kiểm chứng.

| ID phê duyệt | Gói cần cài | Phiên bản đã kiểm chứng | Nguồn + SHA256 nếu có | Tải về/giải nén | Đích cài cục bộ | Rủi ro/ảnh hưởng |
| --- | --- | --- | --- | --- | --- | --- |
| Axx/Bxx/Txx | ... | ... | ... | ... | `<WORKSPACE>\tools` hoặc dự án dưới `projects` | ... |

**Dừng sau P05.** Mẫu yêu cầu: `Tôi phê duyệt cài [ID] vào [WORKSPACE] đúng kế hoạch.` Chỉ chuyển sang cài khi duyệt rõ gói, version, scope; chỉ chuyển sang sản xuất/render khi có phê duyệt riêng. Không bịa checksum/dung lượng; ghi `CHƯA XÁC MINH` và chưa chốt bản nếu thiếu thông tin.

## Kịch bản nghiệm thu

1. Máy không kết nối: P00 BLOCKED, không hỏi thư mục như thể có máy, không ghi software status.
2. Máy kết nối nhưng chưa có thư mục: P01 hỏi path; không dò ứng dụng.
3. Path có workspace sẵn: P02 ghi EXISTING, không ghi đè, rồi P03.
4. Path chưa có workspace: P02 tạo và kiểm chứng, không khởi chạy installer.
5. Có workspace cũ chứa GSAP/Three.js đã xác minh: P03 REUSE_OK; P04 dùng lại khi module resolve thực tế.
6. Có `node_modules` cũ nhưng không tương thích: P03 REUSE_PARTIAL, không đánh dấu đã cài.
7. Không thấy workspace cũ: P03 REUSE_NONE_IN_SCOPE, P04 vẫn dò hệ thống/app trước khi kết luận thiếu.
8. Chỉ Desktop OpenFilm, không dùng CLI/Remotion: A03/A05 hệ thống không mặc định cần cài.
9. Chỉ dùng 2D SVG: B01/B02/B03 có thể TÙY CHỌN CHƯA KÍCH HOẠT.
10. Cần batch Remotion: B03 cùng các dependencies được đưa vào P05 có version/size/nguồn; không tự `npx`.
11. Yêu cầu thuyết minh tiếng Việt: B04 và T01–T06 được kiểm kê, **GPU/PyTorch-CUDA là tuyến ưu tiên**; T07 CPU/ONNX chỉ xét khi T06/P06 có bằng chứng GPU không đáp ứng và user phê duyệt. Không tự tải model/checkpoint khi kiểm tra.
12. Có model cache cũ nhưng không đủ revision/file: T04 CHƯA XÁC MINH hoặc LỖI, không đánh dấu sẵn sàng chỉ vì có thư mục.
13. Giọng nhân bản chưa có xác nhận chủ sở hữu: chỉ sử dụng giọng preset được phép, không tự tạo reference voice.
14. Nếu thiếu quyền ghi path: P02 BLOCKED, không tạo thư mục ở vị trí khác.
15. P05 không có mục thiếu: vẫn báo bảng và dừng chờ phê duyệt giai đoạn sản xuất.

### P04–P05 điều kiện mới B05–B10 (Remotion Master)

| ID | Thành phần | Khi nào đề xuất cài? |
|---|---|---|
| B05 | `react` + `react-dom` | React composition của Remotion Master |
| B06 | `@react-three/fiber` | Remotion Master có cảnh 3D R3F |
| B07 | `@remotion/three` | Remotion Master có `<ThreeCanvas>` |
| B08 | `@remotion/renderer`, `@remotion/cli` | Master render qua Remotion; đã kiểm version/phụ thuộc |
| B09 | `@types/three` | Chỉ khi dự án dùng Three.js + TypeScript |
| B10 | `typescript`, `tsconfig.json` | Chỉ khi dự án dùng TSX |

Tất cả đều được dò qua lockfile/package metadata/path ở P04 **sau P02**. Không thấy package ≠ cần ngay; chỉ khi master/tính năng được duyệt. Đưa từng ID thiếu vào P05 với version/source/hash/size nếu chứng minh được, local path dưới workspace và tác động; mục chưa chốt thì `CHƯA XÁC MINH`. Sau P05 cho người dùng chọn OpenFilm Master (mặc định) hoặc Remotion Master; nếu chuyển master làm phát sinh nhu cầu, làm P04/P05 bổ sung cho các ID liên quan, **không tự cài**. Không thay đổi P00–P03.

### Bổ sung kiểm chứng GPU-first v1.7.0

Nếu người dùng bật VieNeu-TTS, P04 bắt buộc ghi GPU name/vendor, VRAM (total/free nếu đo được), driver, CUDA driver compatibility, Python version, wheel torch/torchaudio + transformers, model/revision và venv đã có. `nvidia-smi` chỉ dùng nếu tồn tại, được chạy read-only và nằm trong phạm vi được duyệt. Không gọi `torch.cuda.is_available()` ở pha read-only nếu lệnh import có tác dụng phụ/chưa được cho phép; runtime probe chỉ ở P06 sau phê duyệt. Nếu không có NVIDIA CUDA, nói rõ GPU không hỗ trợ **theo nhánh v3 Turbo CUDA** (không đồng nghĩa mọi GPU đều không chạy TTS); CPU chỉ là đề xuất cần duyệt. Nếu có GPU nhưng thiếu torch CUDA, ưu tiên lập kế hoạch T05 thay vì cài CPU. GPU không đủ VRAM hoặc lỗi cấu hình: thử giảm batch/chia lời thoại trước, xin duyệt sửa riêng nếu phát sinh tải/cài; chỉ khi GPU không đạt mới trình CPU fallback T07. Ghi trạng thái `GPU_CANDIDATE`, `GPU_RUNTIME_PASS`, `GPU_UNSUPPORTED`, `GPU_INSUFFICIENT`, `GPU_FAILED`, `NOT_VERIFIED`; kèm evidence, không tự đổi backend.

## Bổ sung v1.8.0 — phân biệt audit trước install và runtime sau phê duyệt

P04–P05 chỉ kiểm kê A01 Desktop, A02 CLI **độc lập**, A03 Node, A04 FFmpeg, A05 Chromium. Khi P06 được phê duyệt, tạo runtime profile với lựa chọn `cli` / `desktop-ui` và các capability `openProject`, `inspectFrame`, `renderClip`, `openCanvas`, mỗi mục có `VERIFIED/UNVERIFIED/UNSUPPORTED` và đường dẫn bằng chứng thuộc workspace. Desktop có thể có bộ render đóng gói nhưng không mặc định có lệnh `openfilm` trong PATH. Đối với GUI UI-only, phải xác thực điều khiển dự án/render qua UI từ Remote Desktop Commander; không bịa cờ CLI hoặc kết quả render. Hướng dẫn kỹ thuật: `openfilm-runtime-control/SKILL.md`.

## Chính sách CLI bắt buộc v1.9.0 (ưu tiên so với các chú thích Desktop cũ)

`A02 OpenFilm CLI = CLI_REQUIRED`; `A03 Node >=22.2`, `A04 FFmpeg/FFprobe`, `A05 Chromium/headless` là yêu cầu của CLI path. `A01 Desktop = OPTIONAL VIEWER`. P03 ưu tiên dò lệnh OpenFilm `.cmd` trong workspace cũ có scope và cài system, không chỉ tên app; P04 chỉ đọc metadata và cache; P05 nếu thiếu CLI, liệt kê tải/cài cục bộ và first-run browser, chờ phê duyệt. Không tự phát hành `DESKTOP_UI_VERIFIED` làm thay `CLI_VERIFIED`, không gọi `npx -y openfilm@latest`, không fallback UI-only. Ở Remotion Master, OpenFilm CLI vẫn xử lý dự án previs; Remotion là final encoder theo P08.

---
name: openfilm-moi-truong
description: "Vận hành cổng P00–P05 trên Windows cho Video-hoạt-hình: chọn máy, hỏi đường dẫn, tạo VIDEO_HOAT_HINH_WORKSPACE, dò/tái sử dụng workspace cũ, kiểm tra OpenFilm/GSAP/Three.js/Remotion/VieNeu-TTS và chờ phê duyệt cài phần còn thiếu."
---

# Cổng môi trường Windows P00–P05 — Workspace First, Reuse First

**Cơ sở nguồn**: yêu cầu OpenFilm lấy từ `references/CLI.md`, `references/README.vi.md`; quy trình workspace/reuse và GSAP/Three.js/Remotion và VieNeu-TTS là phần nâng cấp riêng. Phiên bản OpenFilm runtime đã cài trên từng máy là chưa xác minh cho đến khi agent kiểm tra.

## P00. Kết nối máy, xác minh quyền

- Sử dụng công cụ Remote Desktop Commander được người dùng chủ động kết nối (nếu có). Liệt kê máy hiện có; chọn đúng tên/deviceId do user xác nhận, không dùng thiết bị cũ theo trí nhớ.
- Kiểm tra kết nối, Windows, hostname, kiến trúc. Không cài đặt, không ghi vào máy trước khi người dùng chọn thư mục. Không kết nối được → `BLOCKED`.

## P01. Chọn thư mục dự án TRƯỚC kiểm tra software

- Hỏi: `Bạn chọn thư mục dự án nào trên máy [đã xác minh]? (ví dụ D:\du-an\phim-a)`; không hỏi lại nếu đã nêu trong phiên hiện tại.
- Chỉ kiểm tra tồn tại của thư mục cha, tính hợp lệ của đường dẫn, quyền cần thiết và an toàn link/junction/symlink. Kiểm tra tên và thư mục đích; tránh file, đường dẫn hệ thống, UNC/ổ chia sẻ ngoài phạm vi đã duyệt.
- Quy tắc tính root: nếu thư mục được chọn tên `VIDEO_HOAT_HINH_WORKSPACE` (không phân biệt hoa/thường), dùng nó; nếu không, thêm hậu tố `VIDEO_HOAT_HINH_WORKSPACE` đúng một lần.

## P02. Tạo workspace trước kiểm tra phần mềm

- Theo lựa chọn đường dẫn và yêu cầu tạo workspace, tạo root `VIDEO_HOAT_HINH_WORKSPACE` khi chưa có; nếu tồn tại thì mở ở chế độ không phá hủy. Có thể tạo thư mục con trống: `tools`, `cache`, `projects`, `assets`, `renders`, `qc`, `logs`, `reports`; chưa tạo project phim, chưa copy media hoặc cài phần mềm. Phải xác nhận quyền được phép ghi tại root này, không ghi thử vào vùng khác.
- Không xóa, đặt lại quyền ACL, thay tên hoặc ghi đè workspace có sẵn. Nếu root là junction/symlink/reparse point không rõ nguồn hoặc không đủ quyền, `BLOCKED` và xin giải quyết, không tự đi xuyên sang ổ khác.
- Ghi bằng chứng: đường dẫn đã chuẩn hóa, trạng thái `CREATED`/`EXISTING`, các folder con có/thiếu, thời điểm, lỗi nếu có. **Không khẳng định tạo thành công chỉ dựa trên lệnh dự định chạy.**

## P03. Tìm và xác minh workspace CŨ

- Phân biệt **workspace hiện tại vừa tạo ở P02** với các workspace đã được tạo ở *dự án trước*. Tìm theo các root người dùng chỉ định/cho phép; có thể xem các thư mục dự án anh em trong phạm vi cùng parent nếu đã được phép, giới hạn độ sâu và số entry, không quét toàn bộ máy hoặc ổ network.
- Với mỗi `VIDEO_HOAT_HINH_WORKSPACE` cũ: lưu origin path, project name, metadata thời gian, danh mục file được phép đọc (`tools`, `cache`, `package.json`, lockfile, `node_modules` bên trong dự án, Python .venv riêng, VietNeu SDK/ONNX và Hugging Face model cache (chỉ metadata/path)), kiến trúc, phiên bản/nguồn, SHA256 khi cần kiểm chứng. Không chạy binary không rõ nguồn, không thu thập secrets/cookies/tokens.
- **Tái sử dụng có điều kiện**: executables được đóng gói hợp lệ có thể tham chiếu đường dẫn gốc khi tương thích/được phép; dependencies Node `node_modules` có thể phụ thuộc symlink, path, node ABI, lockfile và package manager, nên chỉ dùng khi runtime thực tế xác minh. Không tự sao chép, di chuyển, liên kết, sửa global PATH/registry/permissions. Ưu tiên cache/npm packages từ gói đã xác minh khi phù hợp, không giả định thư mục là bộ cài hoàn chỉnh.
- Không thấy workspace cũ trong vùng được phép → ghi `KHÔNG PHÁT HIỆN WORKSPACE CŨ TRONG PHẠM VI`; tiếp tục P04 kiểm tra software hệ thống/OpenFilm Desktop. Không suy ra là thiếu software chỉ từ việc không thấy workspace cũ.

## P04. Kiểm kê phần mềm và lựa chọn engine

Kiểm kê read-only, không dùng lệnh có thể tải/cài tự động. Xác định chế độ OpenFilm Desktop đóng gói / OpenFilm CLI / OpenFilm build source. Kiểm tra phiên bản, đường dẫn, nguồn, kiến trúc và yêu cầu theo chế độ:

| ID | Thành phần | Bắt buộc khi nào? |
| --- | --- | --- |
| A01 | OpenFilm Desktop | Khi người dùng chạy OpenFilm Desktop; nếu chỉ CLI có thể không cần |
| A02 | OpenFilm CLI | Khi muốn dùng các lệnh CLI; không bắt buộc với Desktop độc lập |
| A03 | Node.js và npm | Khi CLI riêng hoặc dùng Remotion/build source; theo mã nguồn OpenFilm CLI cần Node >=22.2, monorepo >=22.18 |
| A04 | FFmpeg + FFprobe | Khi media/CLI/renderer cần, ưu tiên binary OpenFilm đã đóng gói |
| A05 | Chromium headless/Playwright | Khi CLI/render cần; kiểm tra phiên bản tương thích, bản bundled và cache |
| A06 | Chrome/Edge cho Studio | Chỉ khi mở Studio qua trình duyệt ngoài |
| B01 | GSAP | Cảnh dùng timeline 2D/typography GSAP; gói dự án hoặc vendor cục bộ, không mặc định global |
| B02 | Three.js | Cảnh cần 3D WebGL; kiểm tra package/import map/bundler + GPU/WebGL |
| B03 | Remotion | **Tùy chọn**: React template hoặc batch render, sử dụng runtime React/Node và bộ phụ thuộc đã duyệt |
| B04 | VieNeu-TTS (tên repository `VieNeu-TTS`, Python package `vieneu`) | Khi dự án có lời đọc, hội thoại hoặc thuyết minh tiếng Việt dùng TTS cục bộ; đọc skill `openfilm-vieneu-tts` |
| T01 | Python runtime | Bắt buộc cho nhánh SDK VieNeu-TTS; nguồn upstream khai báo Python >=3.10, phải xác minh bản phát hành và wheel Windows thực tế |
| T02 | `uv` hoặc trình quản lý môi trường Python đã phê duyệt | Chỉ khi cần tạo/khôi phục môi trường TTS, không mặc nhiên cần nếu runtime có sẵn |
| T03 | SDK `vieneu` và phụ thuộc Python | GPU-first: dò SDK/venv; ONNX Runtime chỉ là phụ thuộc riêng nếu CPU fallback được duyệt; không import có nguy cơ tải model ở P04 |
| T04 | Checkpoint/model/cache VieNeu-TTS v3 Turbo | Cần chạy offline; xác minh ID, revision, nguồn license, file đủ, checksum nếu có; chỉ xem metadata, không tải ở P04 |
| T05 | PyTorch CUDA + torchaudio + transformers tương thích GPU | **Ưu tiên/đề xuất bắt buộc khi bật VieNeu-TTS và GPU đáp ứng**; xác minh wheel, CUDA runtime, driver và Python; không tự cài driver/Toolkit |
| T06 | NVIDIA GPU / VRAM / CUDA driver read-only gate | **Bắt buộc đánh giá trước P05** khi bật TTS; trạng thái CANDIDATE không phải GPU_RUNTIME_PASS |
| T07 | ONNX Runtime CPU fallback | **Không cài mặc định**; chỉ trình CPU nếu T06/P06 chứng minh GPU không đáp ứng và user phê duyệt phương án riêng |

- Có thể dùng `Get-Command`, `Get-Item`, `Get-ItemProperty`, đọc `package.json`/lockfile, đọc executable metadata và dò path được phép; không dùng `npx`, `npm install`, `playwright install`, `winget install` hoặc chạy `openfilm render` ở P04. `openfilm doctor` chỉ chạy khi xác minh không ghi/tải tự động, nếu không hoãn.
- `VieNeu-TTS`: không đồng nhất có package `vieneu` với có model đã tải và sử dụng được; không kết luận `TTS_READY` chỉ từ `pip list`/cache folder. Đối chiếu Python>=3.10 ở upstream, Windows wheel và lockfile phiên bản thực tế. Ưu tiên GPU NVIDIA/CUDA cho VieNeu-TTS ngay khi tính năng được bật; không tự dùng ONNX/CPU khi GPU hợp lệ; v4 proprietary/API không thay thế tự động bản v3 Turbo open-source. Quyền sử dụng model tách với license source. Đọc `openfilm-vieneu-tts/SKILL.md` và `references/VIENEU-TTS-WINDOWS.md`.
- `GSAP` và `Three.js` không nhất thiết có installer hoặc CLI riêng: kiểm tra module có thể resolve theo **môi trường dự án**, static local vendor/import map và compatible version. `Remotion` không coi là đã tích hợp vì có tên thư mục: cần CLI/package và render dependency được xác minh; không tự khởi chạy render ở giai đoạn này.
- Nếu Desktop đã render được và có FFmpeg/headless browser đóng gói, không yêu cầu cài bản hệ thống. Không coi binary ngoài PATH là thiếu khi nó tồn tại trong app/workspace; không coi npm/package metadata có tên là đủ chứng minh hoạt động.

## P05. Báo cáo theo ID, khóa cài đặt cho tới phê duyệt

- Xuất bảng đủ A01–A06, B01–B04 và T01–T07 (T01–T07 = `TÙY CHỌN CHƯA KÍCH HOẠT` nếu dự án không dùng VieNeu-TTS): `ĐÃ CÓ–TÁI SỬ DỤNG`, `CÓ SẴN TRONG APP`, `THIẾU CẦN CÀI`, `KHÔNG TƯƠNG THÍCH`, `LỖI`, `CHƯA XÁC MINH`, `KHÔNG CẦN`, `TÙY CHỌN CHƯA KÍCH HOẠT`. Ghi đường dẫn gốc và bằng chứng, kế hoạch sử dụng; các workspace cũ là nguồn **chỉ đọc** nếu không được cấp quyền khác.
- Nếu thiếu thực sự ở chế độ đang cần, trình `ID, phiên bản chốt hoặc chưa xác minh, nguồn chính thức, SHA256 nếu có và kiểm chứng được, size download + giải nén, đường dẫn cài dự kiến dưới WORKSPACE/tools hoặc phụ thuộc trong projects, khả năng tương thích, xung đột, quyền cần, khối lượng tải, chi phí`; không đoán.
- Hiển thị phân biệt 2 phê duyệt: `PHÊ DUYỆT CÀI ID ...` và `PHÊ DUYỆT TRIỂN KHAI DỰ ÁN ...`. Không cài chỉ vì đã cho phép tạo workspace. Dừng chờ. Sau phê duyệt mới thực thi theo phạm vi và nghiệm thu từng ID; không mặc nhiên bắt đầu render.

## Gating, nghiệm thu và điểm dừng

`P00 PASS` xác minh thiết bị; `P01 PASS` nhận đúng path; `P02 PASS` root tồn tại và kiểm chứng; `P03 PASS` đã rà những vị trí được phép và ghi trạng thái kể cả không có workspace cũ; `P04 PASS` bảng có nguồn bằng chứng (mục chưa xác minh được phải chỉ rõ); `P05 PASS` kế hoạch/thành phần thiếu đã trình và dừng. Bất kỳ rủi ro quyền/path hoặc lệnh có thể tự cài/tải -> `BLOCKED` hoặc `CHƯA XÁC MINH`.

Tham khảo `references/P00-P05-WINDOWS.md` để có mẫu bảng, kịch bản kiểm thử và từng lệnh chỉ đọc. `references/P00-P03-WINDOWS.md` là đường dẫn cũ để tương thích và chỉ chuyển hướng quy trình.

## P04/P05 mở rộng Remotion Master (v1.4 — B05–B10)

**Giữ nguyên P00→P01→P02→P03→P04→P05**. Ở P04 sau khi tạo workspace và kiểm tra workspace cũ, tìm thêm (chỉ đọc) các mục **có điều kiện**: `B05 react/react-dom`, `B06 @react-three/fiber`, `B07 @remotion/three`, `B08 @remotion/renderer và @remotion/cli` (hoặc công cụ render phù hợp), `B09 @types/three` và `B10 TypeScript/tsconfig`. Chỉ cần thiết khi chọn **Remotion Master** với React/R3F hoặc TypeScript tương ứng. Nếu người dùng chưa chọn master khi kiểm kê, báo `TÙY CHỌN CHƯA KÍCH HOẠT` và liệt kê những điều kiện sử dụng; sau P05 nếu người dùng bật Remotion Master mà chưa đủ bằng chứng, kiểm lại P04/P05 cho đúng mục thiếu trước khi làm production. Giữ ưu tiên reuse workspace cũ hợp lệ, không tự `npx create-video@latest`, `npm install`, tải browser hay cập nhật package. Kiểm Remotion license theo hoạt động thực, không mặc định MIT. Đọc `references/P00-P05-WINDOWS.md` và `openfilm-render-profiles/references/LICENSE_DEPENDENCIES.md`.

## Sau P05 (không thay đổi thứ tự P00–P05)

Sau P05 cần dừng xin phép cài theo ID. Kể cả khi không thiếu gói, vẫn phải xin duyệt phạm vi **production** riêng. Các pha P06–P21 thuộc `openfilm-production-p06-p21`: P06 nghiệm thu runtime hoặc SKIPPED có chứng cứ khi không cài gì; P07 đọc 7 file đã có; không đọc/kết luận dữ liệu phim trước khi được phép truy cập `SOURCE_DIR`. Không biến giấy phép cài thành giấy phép dựng phim hoặc publish.

## Quy tắc cài đặt VieNeu-TTS v1.7.0

B04 khi được kích hoạt phải qua `GPU_FIRST_POLICY.md`. P03 kiểm tra reuse **venv torch CUDA trước**; P04 xác minh NVIDIA GPU + VRAM + driver/CUDA + Python wheel + phiên bản package chỉ đọc; P05 lập kế hoạch gói GPU T05, model T04 và SDK T03 theo phiên bản chính thức. Nếu GPU không đáp ứng, báo tình trạng và bằng chứng, trình CPU T07 riêng chờ duyệt; không tự hạ cấp backend. P06 sau khi có phê duyệt chỉ chạy test CUDA/giọng trong workspace và ghi rõ backend thực tế; nếu GPU test FAIL báo BLOCKED và xin duyệt sửa/đổi CPU. Chạy `validate_gpu_decision.py` trên report để kiểm quy tắc trước khi đánh dấu TTS_READY.

## OpenFilm runtime gate v1.8.0

P04 đọc metadata A01–A05 không ghi. **P06.08** xác định runtime `CLI_VERIFIED` / `DESKTOP_UI_VERIFIED` / `BLOCKED` bằng thao tác an toàn đã được phê duyệt và hồ sơ `OPENFILM_RUNTIME_PROFILE.json` (`openfilm-runtime-control`). Không đồng nhất tìm thấy app với CLI sẵn. **P06.09–P06.11** nghiệm thu độc lập 7s OpenFilm chuyển động + WAV tone + VTT + render MP4 thật. Không dùng `npx` hoặc UI render ngầm, P18 dự án vẫn chạy riêng. Không có rendering capability thì báo BLOCKED, không chuyển sang Remotion để giả là OpenFilm E2E PASS.

## OpenFilm CLI-first v1.9.0 — cổng bắt buộc

**CLI_REQUIRED**: ở P03 dò `openfilm.cmd`/CLI đã cài qua workspace cũ, project `node_modules/.bin`, hệ thống và mọi source đã cho phép; phân biệt `package.json`/PATH metadata với entrypoint thực. P04 A02, A03 (Node>=22.2), A04 FFmpeg+FFprobe, A05 Chromium cache đều cần được đánh giá cho CLI; A01 chỉ OPTIONAL. Không được `P06 READY` nếu chỉ có Desktop hoặc không có CLI. P05 báo thiếu/tái dùng theo ID, nguồn, phiên bản, SHA256 nếu có, dung lượng bao gồm Chromium first-run, đề xuất cài **cục bộ** và dừng trước download. P06 sau duyệt xác minh CLI `--help`, command cwd, `look/render` trong đúng phim, chạy E2E 7s để nâng capability. Mỗi lệnh CLI phải tuân theo `openfilm-cli-execution/references/CLI_COMMAND_CONTRACT.md`; không đổi hệ thống và không `npx @latest` mặc định. Thêm bảng phân biệt `CLI_READY`, `CLI_BLOCKED`, `CLI_REUSE_CANDIDATE` (candidate không là PASS).

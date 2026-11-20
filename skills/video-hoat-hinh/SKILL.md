---
name: video-hoat-hinh
description: "Điều phối tạo hoạt hình OpenFilm kết hợp GSAP, Three.js, Remotion khi cần và VietNeu-TTS/VieNeu-TTS để tạo giọng tiếng Việt; trước khi dùng máy Windows phải chọn máy, hỏi thư mục dự án, tạo VIDEO_HOAT_HINH_WORKSPACE, kiểm tra/tái dùng môi trường cũ và trình phê duyệt cài đặt."
---

# Video-hoạt-hình v1.11.0 — OpenFilm/Remotion Master + GSAP + Three.js/R3F + VieNeu-TTS

Plugin là **kỹ năng điều phối trong ChatGPT**, KHÔNG phải runtime hay kết nối Remote Desktop Commander tích hợp sẵn. Nguồn đặc tả OpenFilm nằm trong `openfilm-dinh-dang/references/SPEC.md`; bổ sung các kỹ năng GSAP, Three.js, Remotion và VieNeu-TTS; không thay thế OpenFilm hoặc tự cài công cụ. Trên máy tính chỉ thao tác bằng connector được người dùng cấp phép và có bằng chứng thành công.

## Chính sách ưu tiên v1.11.0 — 8 nhóm cấp cao

**Dự án mới bắt buộc dùng `openfilm-macro-bundles/SKILL.md`: 8 macro M0–M7, 99 packet chỉ là việc kỹ thuật/QC nội bộ. Không xin duyệt riêng từng packet hoặc từng Pxx.** User duyệt macro với phạm vi đã thấy, nhân viên AI làm nhiều packet liên tiếp trong lượt High, QC và checkpoint từng packet, tự tiến qua stage đã QC nội bộ; khi hết lượt chỉ nút **Tiếp tục nhóm đã duyệt**. Kết thúc macro mới xin user nghiệm thu kết quả. `openfilm-batch-approval` và một-nút packet của v1.6–v1.10 chỉ **LEGACY** cho dự án đang dở, không áp dụng dự án mới. Phê duyệt đặc biệt không gộp. Giữ P00–P05 chọn máy/path và P05 cài riêng.

## Cổng bắt buộc P00 → P05 khi người dùng muốn thực hiện trên Windows

**Quy tắc thứ tự tuyệt đối: kết nối máy → hỏi thư mục → tạo workspace → tìm workspace cũ → kiểm tra công cụ → báo thiếu/xin duyệt.** Không kiểm tra phần mềm trước khi P02 tạo/xác nhận workspace, ngoại trừ xác minh kết nối và an toàn đường dẫn; không dựng dự án trước khi hoàn tất P05 và được phép.

- **P00 | Kết nối thiết bị:** Dùng Remote Desktop Commander **nếu có và đã được người dùng kết nối** để liệt kê các máy, cho người dùng chọn nếu chưa chọn; xác nhận hostname, deviceId, Windows và trạng thái. Không tự chọn theo lịch sử; lỗi kết nối -> `BLOCKED`.
- **P01 | Hỏi thư mục dự án:** Ngay sau P00, hỏi một đường dẫn tuyệt đối trên **chính máy đã chọn** (ví dụ `D:\VideoDuAn\PhimA`); nếu người dùng đã cho đường dẫn hiện hành, dùng nó, không hỏi lại. Xác nhận path hợp lệ, thuộc phạm vi được phép, không là file/link chuyển hướng. Hỏi thêm thư mục dự án cũ chỉ khi cần để mở rộng phạm vi kiểm tra; không tự quét toàn bộ ổ đĩa.
- **P02 | Tạo/xác nhận workspace:** `WORKSPACE = <PROJECT_DIR>\VIDEO_HOAT_HINH_WORKSPACE`; nếu người dùng chọn chính thư mục mang tên đó thì dùng chính nó, không lồng hai lần. Người dùng đã yêu cầu hành vi tạo root này sau khi chọn đường dẫn: tạo **duy nhất** workspace và thư mục con trống trong phạm vi được phép; nếu tồn tại thì chỉ dùng lại, không ghi đè dữ liệu. Không cài phần mềm, cài dependencies hoặc tạo symlink/junction ở P02. Đọc lại đường dẫn và kết quả tạo, thiếu quyền -> `BLOCKED`.
- **P03 | Dò workspace dự án cũ để tái sử dụng:** Tìm **những thư mục tên `VIDEO_HOAT_HINH_WORKSPACE` từ dự án cũ** trong các root đã được người dùng cho phép, phân biệt với workspace vừa tạo. Kiểm tra manifests/versions, binaries, packages/lockfiles, runtime, cache, license, architecture và khả năng hoạt động bằng phương pháp an toàn. Bản cài cũ phù hợp thì dùng **đường dẫn gốc** nếu tương thích, không copy/cài lại; bản `node_modules`/native modules không mặc nhiên di chuyển được. Nếu không tìm thấy ở phạm vi được phép, ghi `KHÔNG PHÁT HIỆN WORKSPACE CŨ TRONG PHẠM VI`, chưa được suy ra máy thiếu phần mềm.
- **P04 | Kiểm tra phần mềm:** Sau P02/P03 mới kiểm kê `A01 OpenFilm Desktop`, `A02 OpenFilm CLI`, `A03 Node.js/npm`, `A04 FFmpeg/FFprobe`, `A05 Chromium/Playwright`, `A06 Chrome/Edge`, `B01 GSAP`, `B02 Three.js`, `B03 Remotion`, `B04 VieNeu-TTS` (kèm T01–T07 nếu cần TTS), và `B05–B10` React/R3F/Remotion renderer/TypeScript **có điều kiện khi chọn Remotion Master**, thêm nhu cầu phần cứng/dung lượng. **CLI_ONLY_FOR_OPENFILM**: Chỉ dùng OpenFilm CLI A02 đã xác minh làm runtime OpenFilm, dù master là OpenFilm hay Remotion; OpenFilm Desktop A01 chỉ tùy chọn để xem, không được dùng làm đường render thay thế. Node.js A03 >=22.2, FFmpeg/FFprobe A04 và browser/cache A05 là điều kiện cần theo CLI; tìm CLI trong workspace cũ/hệ thống trước, không cài trùng hoặc `npx` tải ngầm. GSAP/Three.js là thư viện theo cảnh, Remotion là tùy chọn; VieNeu-TTS là nhánh lời thoại/thuyết minh tiếng Việt **theo nhu cầu**. Với TTS kiểm tra Python, uv (tùy cách cài), SDK, model/cache, NVIDIA GPU/VRAM/driver và PyTorch CUDA bắt buộc để xét tuyến GPU-first; ONNX/CPU chỉ là phương án dự phòng cần phê duyệt; chỉ gắn cờ thiếu-cần-cài cho tính năng đã lựa chọn. Không khởi tạo SDK ở P04 vì có thể tự tải model.
- **P05 | Báo cáo và xin phê duyệt:** Bảng mỗi ID có `ĐÃ CÓ–TÁI SỬ DỤNG`, `CÓ SẴN TRONG APP`, `THIẾU CẦN CÀI`, `KHÔNG TƯƠNG THÍCH`, `LỖI`, `CHƯA XÁC MINH`, `KHÔNG CẦN`, `TÙY CHỌN CHƯA KÍCH HOẠT`. Nếu thiếu, trình phiên bản dự kiến, nguồn chính thức, checksum nếu xác minh được, dung lượng dự kiến, path cài **bên trong workspace**, xung đột, phụ thuộc, ảnh hưởng và **ID để người dùng phê duyệt**. Dừng; không tải/cài/gọi `npx`/chạy render/đụng driver/OS khi chưa duyệt các ID và phạm vi tương ứng. Nếu không có mục cần cài vẫn báo kết luận và xin duyệt rõ trước khi bước dựng phim trên máy.

**Đọc `openfilm-moi-truong/SKILL.md` và `openfilm-moi-truong/references/P00-P05-WINDOWS.md` để áp dụng chính xác.** Mốc P02 là ngoại lệ có ghi thư mục theo yêu cầu người dùng; P03–P05 chỉ đọc. Không có connector hoặc quyền trên máy thì cung cấp kế hoạch thay vì báo giả đã kết nối/tạo thư mục. Nếu không có UI nút phê duyệt thật, xin duyệt qua chat, không hứa một nút độc lập.

## Phân công các kỹ năng

| Nhu cầu | Kỹ năng |
| --- | --- |
| Máy Windows, thư mục, kiểm tra, reuse, phê duyệt | `openfilm-moi-truong` + `references/P00-P05-WINDOWS.md` |
| Mọi thao tác OpenFilm bằng CLI (bắt buộc) | `openfilm-cli-execution` + `openfilm-runtime-control` |
| Kịch bản, storyboard, bố cục | `openfilm-kich-ban`, `openfilm-canvas` |
| Chuẩn OpenFilm / frame theo thời gian | `openfilm-dinh-dang`, `openfilm-animation` |
| Chữ, nhân vật 2D, easing, timeline | `openfilm-gsap` |
| Phối cảnh 3D, camera, vật liệu/ánh sáng | `openfilm-threejs` |
| Template React/clip hàng loạt (tùy chọn) | `openfilm-remotion` |
| Lời thoại, thuyết minh, đa nhân vật tiếng Việt, audio WAV | `openfilm-vieneu-tts` + `references/GPU_FIRST_POLICY.md` (GPU-first, CPU có điều kiện); trước `openfilm-media` và `openfilm-qc-render` |
| FilmData/timeline và provenance | `openfilm-filmdata` |
| Bộ chọn master, file handoff | `openfilm-hybrid-master` |
| React Three Fiber / WebGL ANGLE | `openfilm-remotion-r3f` (Remotion Master) |
| WAV timing, phụ đề tiếng Việt, ducking | `openfilm-audio-subtitles` |
| Profile, hiệu năng, lock/license | `openfilm-render-profiles` |
| QC20, deterministic và smoke 5 giây | `openfilm-qc-advanced` |
| Dự án tham chiếu 90 giây | `openfilm-sample-90s` |
| Media, hậu kỳ, dựng phim, QC | `openfilm-media`, `openfilm-timeline`, `openfilm-color`, `openfilm-qc-render` |
| Nạp 7 tài liệu kịch bản | `openfilm-script-input` |
| Điều phối các cổng P06–P21 | `openfilm-production-p06-p21` |
| Checkpoint, phê duyệt, sửa lỗi và phục hồi | `openfilm-checkpoint-approval` |
| **8 macro-bundle M0–M7, nguồn điều phối mặc định** | **`openfilm-macro-bundles`** |

## Lựa chọn engine và luồng xuất

**OpenFilm Master (mặc định)** giữ OpenFilm làm timeline và thành phẩm; **Remotion Master (chỉ khi được người dùng chọn và môi trường đã được phê duyệt)** sử dụng OpenFilm cho thiết kế/kiểm tra/previs, Remotion làm timeline master/encode cuối. Hai mode trao đổi qua file adapter: không tự chuyển `film.html` thành JSX, không giả định API có sẵn. Dùng `openfilm-hybrid-master` + `openfilm-filmdata` để thống nhất integer frames và nguồn asset. Ở OpenFilm Master, mặc định dùng HTML/CSS/SVG trong cảnh OpenFilm; chọn GSAP nếu có chuyển động 2D phức tạp, Three.js nếu cần 3D thực; kết hợp GSAP + Three.js khi cần điều khiển camera/đối tượng bằng một `t` duy nhất. Trong `window.film.frame(t)`, đầu ra ở cùng `t` phải giống nhau dù scrub tiến/lùi; không chạy tự động `requestAnimationFrame`/`setInterval` khi có host, không phụ thuộc trạng thái frame trước. VieNeu-TTS **không phải engine render video**: nhánh tạo giọng sinh WAV cục bộ rồi nạp vào track âm thanh OpenFilm, đồng bộ timeline bằng thời lượng/đo thực tế; chuẩn hóa văn bản, chia câu, tạo voice theo nhân vật, nghe duyệt và làm VTT/SRT từ timestamp có bằng chứng. Chỉ tải model sau phê duyệt; voice cloning chỉ với sự đồng ý và quyền sử dụng giọng rõ ràng, ưu tiên preset voices. Nếu Remote Desktop Commander không chuyển âm thanh, xuất đoạn QC để người dùng tải/gửi vào chat; không được giả vờ đã nghe.

Remotion **không phải plugin engine bên trong OpenFilm**. Với OpenFilm Master, Remotion chỉ render clip trung gian khi cần; với Remotion Master, Remotion làm composition/timeline cuối (React/GSAP/R3F/audio) và OpenFilm chỉ sản xuất previs/assets. Khi P05 chưa có quyết định master, giữ OpenFilm Master mặc định; nếu chọn Remotion Master nhưng B05–B10 chưa được audit đầy đủ, bổ sung kiểm kê P04/P05 cho danh mục phát sinh trước khi dựng. Không tự cài, không coi TSX đã render, không giả định chuyển source trực tiếp.

**ĐIỀU KIỆN VIE NEU GPU-FIRST v1.7.0:** Nếu bật VieNeu-TTS, mặc định đề xuất GPU NVIDIA/PyTorch-CUDA, dù chỉ tạo câu ngắn. P04 dò read-only GPU, CUDA driver, VRAM, Python/torch wheel, cache/model/venv tái sử dụng; P05 liệt kê gói GPU tương thích, không phê duyệt thì dừng. P06 cần probe CUDA và tạo WAV mẫu thật sau chấp thuận; P12 chỉ tổng hợp bằng backend GPU đã được nghiệm thu, không chấp nhận SDK âm thầm chạy ONNX/CPU. Chỉ **đề xuất** CPU nếu GPU không có, không tương thích, thiếu tài nguyên sau cấu hình hợp lý, hoặc lỗi có bằng chứng và không sửa được trong phạm vi đã duyệt; chuyển CPU phải nhận phê duyệt mới có ID. Xem `openfilm-vieneu-tts/references/GPU_FIRST_POLICY.md` và `openfilm-moi-truong/references/VIENEU-TTS-WINDOWS.md`. Bổ sung gate GPU vào gói việc High và checkpoint, không tính GPU_READY chỉ từ `nvidia-smi` hoặc `torch` đã cài.

Sau P05, khi người dùng phê duyệt giai đoạn sản xuất: brief → beat → storyboard → shots → tài sản → VietNeu-TTS (nếu bật) và nghiệm thu lời đọc → voice/SFX → timeline → chỉnh màu → kiểm tra đầu/giữa/cuối và random seek → render → nghiệm thu MP4. Mọi thay đổi ngoài vùng dự án được phép đều phải báo và được duyệt riêng. Không coi cài đặt thành công là render thành công; luôn kiểm chứng file/metadata và kết quả xem trước thực tế.

## Cổng P06–P21, chạy nội bộ trong M0–M7 (v1.11.0)

**Sau P05 phải DỪNG để người dùng duyệt các ID cài đặt và/hoặc phạm vi làm việc.** Phê duyệt nâng cấp plugin **không** là phê duyệt thao tác trên Windows; phê duyệt cài đặt P05 **không** là phê duyệt chạy render. Khi người dùng đã duyệt bước tiếp theo, đọc `openfilm-production-p06-p21/SKILL.md` và `references/P06-P21-WORKFLOW.md` để chạy cổng tương ứng. Giữ nguyên thứ tự P00–P05 đã có, không được lấy shortcut bằng cách đọc phần mềm trước P02.

**Kịch bản đầu vào có thể đã có sẵn** trong một thư mục nằm bên trong `VIDEO_HOAT_HINH_WORKSPACE`, gồm 7 file: `KICH_BAN_HOAN_CHINH.md`, `COT_TRUYEN.md`, `NHAN_VAT.md`, `LOI_THOAI.md`, `DANH_SACH_CANH.csv`, `HUONG_DAN_HINH_ANH_AM_THANH.md`, `BAO_CAO_NGHIEM_THU.md`. P07 phải mở **file thật** trong đường dẫn được cho phép, đọc nội dung và kiểm tra mâu thuẫn; không viết lại kịch bản khi nguồn đã được duyệt và không bịa nội dung chỉ từ ảnh tên file. Giữ 7 tệp gốc bất biến, mọi bản sửa cần phê duyệt và nằm trong project working copy. `BAO_CAO_NGHIEM_THU.md` là nghiệm thu **kịch bản**, không chứng minh file phim hay nghiệm thu QC20.

| Phase | Công việc chính | Evidence tối thiểu |
|---|---|---|
| P06 | Cài/nội kiểm các ID đã phê duyệt ở P05 hoặc bỏ qua cài nếu môi trường đã đạt | Báo cáo môi trường thực |
| P07 | Đọc đủ 7 file và kiểm kê/mapping cảnh ↔ thoại ↔ nhân vật | INPUT_AUDIT + SOURCE_MANIFEST |
| P08 | Chốt master engine và phong cách / FPS / tỷ lệ | PRODUCTION_PROFILE đã duyệt |
| P09 | FilmData, shot/dialogue ID và nguồn asset | film.json + validator |
| P10 | Character/Style Bible, storyboard | Storyboard từng shot đã duyệt |
| P11 | Asset SVG/3D/font/background | Assets có thật + license/hash |
| P12 | VieNeu-TTS tạo WAV từng lời thoại và nghe QC | WAV + FFprobe + nghe thật |
| P13 | Cập nhật timeline theo WAV thật, SRT/VTT | Audio-sync report |
| P14 | Chuyển động 2D GSAP theo shot | Scene code + preview frame QC |
| P15 | Cảnh 3D Three.js/R3F nếu có | WebGL preview / skip có lý do |
| P16 | Preview/OpenFilm previs, nghiệm thu shot | Shot QC + previews |
| P17 | Lắp ráp master timeline, color, thoại, SFX/nhạc | Timeline report |
| P18 | Smoke 5 giây hình/tiếng/subtitle | MP4 thật + FFprobe + xem/nghe |
| P19 | Render draft toàn phim | Draft MP4 + log + metadata |
| P20 | QC20, ghi issue và sửa đúng phạm vi sau duyệt | QC20 report + issue status |
| P21 | Xuất và kiểm MP4 master, phụ đề, source, manifest | FINAL_MASTER.mp4 và nghiệm thu cuối |

## Checkpoint / duyệt ở cấp macro (v1.11.0)

- `PRODUCTION_STATUS.json` giữ trạng thái 16 stage; `WORK_UNIT_INDEX.json` giữ 99 mẫu packet materialize và `macroBundles[]` M0..M7, phê duyệt và hash, QC mỗi packet. **Stage QC PASS trong cùng macro không đồng nghĩa user đã nghiệm thu**; dùng `macroInternalGate` khi có approval plan macro có thật. Chỉ user click nghiệm thu macro thì macro và các packet mới PASS với acceptance ID.
- Một lượt High chạy **nhiều packet** trong nhóm đã duyệt, không dừng sau từng file/từng shot để hỏi. Hết lượt: lưu checkpoint, một nút `Tiếp tục nhóm đã duyệt` sau khi xác minh rev/device/workspace/hash. Không thể tự động tạo lượt chat tiếp theo.
- Mỗi giai đoạn P06–P21 giữ kiểm chứng riêng; P08/P10 quyết định hình, P12/P13 nghe giọng, P21 final vẫn cần quyết định/phê duyệt người dùng khi thích hợp. Đọc `openfilm-macro-bundles/SKILL.md` trước các chỉ dẫn phiên bản cũ.
- Cấm phê duyệt chung cho PACKAGE_INSTALL, MODEL_DOWNLOAD, BROWSER_DOWNLOAD, GPU_TO_CPU_FALLBACK, VOICE_CLONING, EXTERNAL_PROVIDER, PAID_ACTION, DELETE, PUBLISH và OUT_OF_SCOPE. Không bịa file/MP4/tiếng đã nghe.

## Quy tắc OpenFilm v1.8.0: 5 cổng sửa lỗi ưu tiên hơn mô tả cũ

1. **P06 Runtime Capability Gate:** Sau P05 đã duyệt, không suy ra có CLI từ việc thấy OpenFilm Desktop. Đọc `openfilm-runtime-control/SKILL.md`, tạo `reports/openfilm/OPENFILM_RUNTIME_PROFILE.json` dựa trên probe có evidence. `CLI_VERIFIED` mới cho phép thực thi OpenFilm; `DESKTOP_UI_VERIFIED` không còn là runtime hợp lệ; `UNVERIFIED/BLOCKED` không chạy render hay coi là PASS. Đừng gọi `npx`, `openfilm doctor`, browser nếu chưa xác minh tác dụng phụ; runtime profile trỏ evidence và revision thiết bị/đường dẫn.
2. **P06 Early E2E Probe (độc lập):** `openfilm-smoke-e2e/SKILL.md` có bài thử 7 giây dùng một cảnh HTML động, WAV test tone tạo cục bộ, WebVTT + `film.html`. Chỉ chạy sau phê duyệt ghi/render, không cài gì mới; FFprobe, xem và nghe thật rồi mới `E2E_PASS`. WAV test tone chứng minh audio pipeline, **không chứng minh chất lượng VieNeu**. Nếu không điều khiển renderer được → BLOCKED, đề xuất cài/xác minh CLI và phụ thuộc để user duyệt, không giả PASS. P18 smoke master dự án vẫn bắt buộc, E2E P06 không thay P18.
3. **P09 FilmData → Early OpenFilm Skeleton:** Ngay sau FilmData hợp lệ, trước P10/P14/P16, chạy `openfilm-runtime-control/references/bootstrap_openfilm.py` sau phép tạo/ghi đúng project: khởi tạo `openfilm/film.html` + `scenes/<shot-id>.html` placeholders theo ID/thời gian thật, tuyệt đối không ghi đè. Phải báo `PLACEHOLDER`, chưa phải cảnh đã hoàn thiện, không duyệt preview P16 cho đến khi hết placeholder. P17 hoàn thiện/khóa timeline hiện hữu, không khởi tạo lần đầu.
4. **P10 Canvas Option Gate:** Trình `CANVAS_MODE=FILE_STORYBOARD` (mặc định) hoặc `OPENFILM_CANVAS` (chỉ nếu runtime hỗ trợ + người dùng duyệt). `openfilm canvas apply` không dùng khi chưa xác minh bản CLI/Studio thực. Canvas chỉ chuẩn bị bố cục/node; không tự Make, tải, gọi nhà cung cấp video, TTS hoặc dịch vụ tính phí. Nếu Canvas không khả dụng, tiếp tục storyboard file, ghi `SKIPPED_CANVAS` có lý do, không chặn phim.
5. **P08/P12 Voice Source Lock:** Khi dự án chọn VieNeu-TTS, `reports/tts/VOICE_SOURCE_LOCK.json` ghi `source=vieneu-local`, backend GPU CUDA/PyTorch đã nghiệm thu (CPU chỉ theo quy tắc T07), model revision/voice preset và phạm vi; mặc định `openfilm get voice`, `openfilm canvas tts`, `openfilm get tts`, TTS từ Studio/provider ngoài đều `DENY`. Chỉ đổi sang provider khác khi có phê duyệt riêng, không tự tạo phí, không tự chuyển CPU. OpenFilm nhập **WAV đã tạo/duyệt từ VieNeu**, không tổng hợp lại. Đọc `openfilm-vieneu-tts/references/VOICE_SOURCE_POLICY.md` và validator.

**Bắt buộc phân gói High + nút phê duyệt:** P06.08–P06.11, P08.05, P09.06, P10.06–P10.07, P12.08, P14.06, P16.06, P17.07 là các packet nội bộ với kế hoạch, evidence và checkpoint; chỉ hiển thị nút ở cấp bundle đã chốt phạm vi (nếu host hỗ trợ). Không coi việc user phê duyệt nâng cấp plugin là cho phép ghi/cài/render trên máy Windows. Khi kỹ năng cũ nêu trái chính sách này, chính sách v1.8.0 ưu tiên.

## Ưu tiên chính sách CLI v1.9.0

**CLI_ONLY_FOR_OPENFILM** thay thế mọi mô tả cũ cho phép OpenFilm Desktop UI-only làm renderer. Đọc `openfilm-cli-execution/SKILL.md` trước P04/P06/P09/P10/P14/P16/P17/P18/P19/P20/P21. A02 CLI là `CLI_REQUIRED` tại P04–P05; thiếu A02/Node/FFmpeg/browser đủ điều kiện -> báo ID + phê duyệt, không chuyển Desktop làm fallback. P06.08 xác minh mode=cli và cwd, P06.09–11 E2E qua CLI. P09 tạo skeleton file (không gọi CLI open để tạo ngoài scope); P10 Canvas có thể gọi `openfilm canvas` sau duyệt; P14–P16 `openfilm look`; P18/P19/P21 `openfilm render` bằng CLI trong thư mục `film.html`. Studio UI chỉ xem/chỉnh sửa qua `openfilm open` sau phê duyệt và không phải điều kiện phát hành. Mỗi lần gọi phải có command event và checkpoint gắn ID, log/exitCode/artifacts, không gọi `npx` tự tải. Với Remotion Master, OpenFilm CLI làm previs còn Remotion xuất final; giữ one-click approvals, GPU-first VieNeu và 7 file đầu vào. Không chạy trên PC chỉ vì đã cập nhật plugin.

## v1.11.0 — 8 macro thay phê duyệt riêng Pxx

M0 P00–P06 (trong đó P00–P05 là cổng lựa chọn/kiểm kê), M1 P07–P09, M2 P10–P11, M3 P12–P13, M4 P14–P16, M5 P17–P18, M6 P19–P20, M7 P21. `openfilm-macro-bundles/SKILL.md` là nguồn quyết định phê duyệt và lịch thực thi cho dự án mới. Legacy BUNDLE_POLICY/99 template chỉ để lưu hồ sơ kỹ thuật. Số lượt High không được cam kết; khi hết lượt chỉ tiếp tục macro đã duyệt. Phê duyệt đặc biệt và nghiệm thu final vẫn riêng.

## v1.12.0 — Mandatory Visual Inspection & Quality Gate
**ƯU TIÊN CAO HƠN MỌI HƯỚNG DẪN CŨ**: Trong M2, M4, M5, M6, M7 phải đọc `openfilm-visual-inspection/SKILL.md` và chính sách `VISUAL_QC_POLICY.json`; **không PASS/ACCEPT** chỉ từ JSON, log, FFprobe, ảnh tồn tại trên máy hoặc file screenshot chưa được đưa vào ngữ cảnh nhìn ảnh của ChatGPT. Dùng Remote Desktop Commander `read_file`/`read_multiple_files` (PNG/JPEG/WebP) và thực sự quan sát image content; nếu công cụ chỉ trả text/base64 hay thiếu quyền thì `VISUAL_BLOCKED`, xuất ảnh thật để user upload. M2 xem storyboard, nhân vật, bối cảnh/assets; M4 xem từng frame OpenFilm CLI look; M5/M6/M7 kiểm frame trích từ **MP4 đã render tương ứng**. Ghi nhận xét thị giác riêng từng shot, lưu hash nguồn/ảnh và receipt, sửa có phạm vi rồi xem ảnh lại; không tự nhận đã xem toàn phim từ frame mẫu. Phê duyệt vẫn **một macro**, không thêm nút mỗi frame; audio VieNeu vẫn GPU-first và QC nghe riêng. `validate_macro_event.py` chặn `ACCEPT_MACRO` và `ACCEPT_AND_APPROVE_NEXT_MACRO` nếu chưa có Visual QC report thật được xác minh.

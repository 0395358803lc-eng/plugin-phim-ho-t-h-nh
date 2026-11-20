---
name: video-hoat-hinh
description: "Điều phối hoạt hình từ kịch bản đến V01 rồi sửa theo phản hồi: OpenFilm CLI, GSAP/Three.js, VieNeu-TTS GPU và Remotion khi được chọn."
---

# Video-hoạt-hình — Finish First v1.14.1

Đây là plugin kỹ năng điều phối, không chứa runtime, model hay connector máy tính. Dùng công cụ thực có trong phiên và báo đúng bằng chứng. Mặc định dự án mới dùng `FINISH_FIRST_USER_REVIEW`: hoàn thành V01, bàn giao, rồi chỉnh V02/V03 theo phản hồi. Kiểm tra kỹ thuật bảo đảm file dùng được; QC20, Visual QC, nghe chấm từng câu và nghiệm thu từng macro không chặn luồng mặc định.

## Quyền và môi trường P00–P05, thực thi P06

Chính sách `CLI_ONLY_FOR_OPENFILM` giữ OpenFilm CLI làm đường thực thi. Không xin duyệt riêng từng packet hoặc từng stage trong phạm vi sản xuất đã cấp.

Dùng thiết bị và workspace người dùng đã chọn trong phiên; chỉ hỏi thông tin còn thiếu. Theo thứ tự: xác minh kết nối/thiết bị → xác nhận đường dẫn → tạo hoặc dùng lại workspace → tìm runtime cũ trong phạm vi đã biết → kiểm kê phần cần dùng → xử lý mục còn thiếu. Không quét toàn ổ đĩa hay ghi vào dự án cũ để làm bài thử.

Đọc [môi trường](../openfilm-moi-truong/SKILL.md), [CLI](../openfilm-cli-execution/SKILL.md) và [runtime control](../openfilm-runtime-control/SKILL.md). Kiểm executable, cwd, phiên bản và dependencies đang có. OpenFilm CLI là đường thực thi OpenFilm; Desktop/Studio chỉ để xem/chỉnh sửa tùy chọn. Không suy ra CLI có sẵn từ việc thấy Desktop; không dùng `npx` gây tải ngầm. Tái sử dụng runtime tại vị trí gốc; không mặc định copy được node_modules/native modules.

Một yêu cầu sản xuất đã xác định phạm vi có thể cấp quyền cho M1–M7 trong một lần. Không xin lại quyền đã có. Các thao tác PACKAGE_INSTALL, MODEL_DOWNLOAD, BROWSER_DOWNLOAD, GPU_TO_CPU_FALLBACK, VOICE_CLONING, EXTERNAL_PROVIDER, PAID_ACTION, DELETE, PUBLISH và OUT_OF_SCOPE cần quyền riêng nếu chưa được cấp. Thiếu runtime thì báo đúng thành phần và phạm vi cần bổ sung; không tự đổi engine hay backend.

## Bảng điều phối kỹ năng

| Nhu cầu / đầu ra | Kỹ năng chịu trách nhiệm |
|---|---|
| Máy, workspace, runtime tái sử dụng | openfilm-moi-truong |
| Mọi lệnh OpenFilm, command log và capabilities | openfilm-cli-execution, openfilm-runtime-control |
| Nhập bảy tài liệu, giữ hash nguồn | openfilm-script-input |
| Brief, beats, cảnh và lời thoại | openfilm-kich-ban |
| Master engine và adapter giữa engine | openfilm-hybrid-master |
| Shot ID, integer frames, dialogues và provenance | openfilm-filmdata |
| Storyboard, bố cục, Canvas nếu có | openfilm-canvas |
| Tài sản có thật, license, nguồn media | openfilm-media |
| PNG tạo trong chat cần chuyển vào workspace | openfilm-image-zip-handoff |
| Chuẩn film.html, media tracks và scene API | openfilm-dinh-dang |
| Cảnh HTML/CSS/SVG theo thời gian | openfilm-animation |
| Nhân vật/chữ/camera 2D với easing | openfilm-gsap |
| Camera, ánh sáng, vật liệu và chuyển động 3D | openfilm-threejs |
| React composition, clip hoặc master được chọn | openfilm-remotion |
| Three.js/R3F trong Remotion, WebGL/ANGLE | openfilm-remotion-r3f |
| WAV tiếng Việt, preset voice, CUDA/model local | openfilm-vieneu-tts |
| WAV timing, VTT/SRT, gain/ducking | openfilm-audio-subtitles |
| Trim, at, offset, transition và lớp âm thanh | openfilm-timeline |
| Phối màu/LUT khi phim cần | openfilm-color |
| FPS/kích thước/codec/tài nguyên và lock/license | openfilm-render-profiles |
| Triển khai P06–P21 và đầu ra từng bước | openfilm-production-p06-p21 |
| 8 macro, quyền phạm vi, scheduler xuyên macro | openfilm-macro-bundles |
| 99 mẫu packet và materialization | openfilm-high-workpackets |
| Checkpoint, hash, lỗi và tiếp tục | openfilm-checkpoint-approval |
| Tiếp tục/xem/chấp nhận/yêu cầu sửa qua host | openfilm-oneclick-approval |
| Đọc approvalBundles cũ, chỉ tương thích | openfilm-batch-approval |
| Bài thử runtime khi cần chẩn đoán | openfilm-smoke-e2e |
| Dữ liệu tham khảo 90 giây, chưa phải video thật | openfilm-sample-90s |
| Đánh giá hình ảnh theo yêu cầu | openfilm-visual-inspection |
| Đánh giá bản render theo yêu cầu | openfilm-qc-render |
| QC20, determinism, random seek theo yêu cầu | openfilm-qc-advanced |

## Trách nhiệm của từng công cụ

**OpenFilm Master mặc định:** OpenFilm quản lý timeline và xuất MP4 qua CLI. Cảnh là HTML/CSS/SVG; GSAP điều khiển chuyển động 2D khi cần. Three.js bổ sung 3D thực, không bắt buộc cho phim 2D. Chuẩn scene: `window.film = {duration, frame(t)}`; cùng t phải cho cùng kết quả khi scrub tiến/lùi. Dùng timeline GSAP paused rồi seek(t); không để setInterval/requestAnimationFrame tự chạy dưới host. Camera và vật thể Three.js cũng tính từ t, tránh cộng dồn transform.

**Remotion:** chỉ chọn khi nhu cầu React/template/composition hoặc người dùng đã chọn. Với OpenFilm Master, Remotion có thể tạo clip trung gian; với Remotion Master, OpenFilm CLI làm previs/assets, Remotion encode cuối. Hai engine trao đổi file + FilmData, không tự biến film.html thành JSX. Chỉ dùng React/R3F/renderer/browser đã có hoặc được cấp quyền cài.

**VieNeu-TTS:** tạo WAV, không render video. Chuẩn hóa tiếng Việt, chia theo thoại/cảnh, khóa preset/voice và model. Đo WAV thật rồi tính frame, captions và track audio. GPU-first nghĩa là model lẫn codec thực chạy CUDA, không chỉ nvidia-smi báo có card. Không tự chuyển CPU; không yêu cầu người dùng nghe từng câu trước dựng.

## Quy trình sản xuất

1. Đọc nguồn thật. Nếu có sẵn bảy tài liệu thì giữ bất biến, tạo working copy khi cần sửa. Nếu nhiệm vụ yêu cầu tạo dự án mẫu, viết kịch bản riêng và ghi rõ nguồn do tác vụ tạo.
2. Chọn profile/master phù hợp phạm vi; lập FilmData với ID ổn định, thời gian integer frames. Validator bắt gap, overlap, dialogue ngoài cảnh và đường dẫn sai.
3. Tạo skeleton film.html sớm theo shot ID; đánh dấu placeholder và thay bằng cảnh thật trước render. Storyboard và character/style bible quy định bố cục, chuyển động, màu và continuity.
4. Tạo/nhập assets có nguồn và hash. PNG từ chat cần ZIP thật nếu không có đường truyền bytes; file thiếu chặn bước dùng asset đó, không mở cổng nghiệm thu thẩm mỹ.
5. VieNeu GPU sinh WAV; phụ đề dùng thời lượng đo thật. Chuyển động theo t, asset paths tương đối, font tiếng Việt có sẵn.
6. Lắp timeline, kiểm file phụ thuộc và render toàn phim bằng CLI đã xác minh. Không render thêm master trùng nội dung nếu V01 đáp ứng profile.
7. Giải mã MP4, kiểm stream/kích thước/FPS/duration/audio theo cấu hình. Lưu hash, log và manifest; giao link video thật cùng source/phụ đề.
8. Phản hồi scene/audio/subtitle/effect tạo revision có targetIds; giữ V01 và hash, xuất V02 ở path mới. Chỉ người dùng mới quyết định chấp nhận.

## Trạng thái và tiếp tục

Giữ 8 macro M0–M7 và 99 ID packet. Packet là việc kỹ thuật nội bộ, không phải 99 lần xin duyệt. `OUTPUT_READY` là file dùng được; `DELIVERED_FOR_REVIEW` là đã bàn giao; `USER_ACCEPTED` chỉ từ phản hồi thật. `FAILED_TECHNICAL` chặn bước phụ thuộc file hỏng; lỗi thẩm mỹ được ghi để sửa theo phản hồi.

Checkpoint thiếu productionMode hoặc mang phiên bản cũ không tự trở thành Finish First. Đọc [migration](../openfilm-macro-bundles/references/OPERATIONS.md), sao lưu byte gốc, chuyển đổi rồi đối chiếu quyền cũ. Migration không tự cấp quyền. Lưu checkpoint sau đầu ra, tiếp tục scope cũ trong lượt sau; không tự tạo lượt chat hay chạy nền.

Chi tiết thực thi: [production](../openfilm-production-p06-p21/SKILL.md), [playbook](../openfilm-production-p06-p21/references/PRODUCTION_PLAYBOOK.md), [macro](../openfilm-macro-bundles/SKILL.md).

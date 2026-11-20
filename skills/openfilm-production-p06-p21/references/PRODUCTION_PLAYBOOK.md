# Production playbook — v1.14.1

Hướng dẫn thực thi trong phạm vi đã được người dùng cấp. Không có yêu cầu chấp nhận từng Pxx, packet, frame hay take. P18/P20 là chẩn đoán/đánh giá tùy chọn; không thêm chúng vào đường phụ thuộc mặc định của P19/P21.

## Tổ chức dự án và nguồn

Dùng root thật trên thiết bị đã chọn. Tách `source/` bất biến, `assets/`, `audio/`, `captions/`, `scenes/`, `reports/`, `renders/`, `film.json`, `film.html`. Revision có thư mục source riêng hoặc manifest hash đủ để tái tạo V01/V02. Không dùng thư mục làm outputPaths: liệt kê các file cụ thể.

Bảy tài liệu: KICH_BAN_HOAN_CHINH.md, COT_TRUYEN.md, NHAN_VAT.md, LOI_THOAI.md, DANH_SACH_CANH.csv, HUONG_DAN_HINH_ANH_AM_THANH.md, BAO_CAO_NGHIEM_THU.md. Đọc nội dung, không suy diễn từ tên file. `audit_seven_files.py` kiểm cấu trúc/encoding/hash; người điều phối còn phải đối chiếu nhân vật, cảnh và thoại. Báo cáo nghiệm thu kịch bản không phải acceptance video.

## M1: profile và FilmData

Ghi masterEngine, FPS, width/height, durationInFrames, style, âm thanh cần/không cần và lý do. `shots[]` có id, startFrame, durationInFrames, type=2d/3d, scene. `dialogues[]` có id, shotId, speaker, text, startFrame, endFrame, audio. Tất cả frame là số nguyên; shots liên tục; mỗi thoại nằm trong shot. Đo WAV xong thì cập nhật duration/interval thay vì kéo thoại theo dự tính ban đầu.

Chạy validator có sẵn: `python validate_filmdata.py film.json --check-assets PROJECT_ROOT`. Skeleton từ `bootstrap_openfilm.py` chỉ tạo file chưa tồn tại và chưa đại diện cảnh hoàn thành. Không render V01 với placeholder hoặc thiếu asset.

## M2: storyboard và assets

Mỗi shot ghi cỡ cảnh, vị trí nhân vật, bố cục, action, nhịp đầu/cuối và transition. Character bible giữ tỷ lệ, palette, costume, phụ kiện và voice; style bible giữ background, ánh sáng và typography. Canvas mặc định FILE_STORYBOARD; chỉ dùng OPENFILM_CANVAS nếu capability được xác minh và trong scope. Không tự gọi Make/provider/TTS từ Canvas.

Assets có ID, source/license, path, hash, kích thước hoặc thông số mesh/material. SVG/HTML dùng trực tiếp nếu pipeline hỗ trợ; PNG tạo bằng image tool cần bytes thật và handoff manifest. Không bắt tạo ảnh raster nếu phim được thiết kế bằng SVG/3D. Theo dõi missing assets theo shot để sửa đúng phần phụ thuộc.

## M3: lời thoại và phụ đề

Đọc openfilm-vieneu-tts và GPU_FIRST_POLICY. Tái sử dụng venv/model/codec đã có; audit path trước khởi tạo SDK. Khóa mạng/download khi làm bài thử local-only. Kiểm torch CUDA, GPU/VRAM và device thật của backbone lẫn codec sau inference; lưu version, model hash/revision, voice, seed và lệnh. NVIDIA có sẵn không đủ chứng minh inference CUDA.

Sinh WAV theo dialogue/scene bằng preset được chọn. Đo sample rate, frames/duration, channel và khả năng decode; lưu SHA256. Không im lặng chuyển CPU/provider, không cloning nếu chưa có quyền. Giữ WAV nguồn, dùng gain/ducking ở timeline khi cần.

Captions VTT/SRT: cue tăng dần, start < end, không vượt shot/audio, chữ UTF-8. Timestamp theo căn chỉnh có bằng chứng; nếu chia câu theo tỷ lệ duration thì ghi rõ chưa có forced alignment cấp từ. Burn-in hoặc subtitle track theo profile; chỉ chứa VTT mà không đưa vào render không chứng minh phụ đề xuất hiện. Không lấy điểm QC nghe làm điều kiện tạo cảnh.

## M4: cảnh hoạt hình

Dùng OpenFilm scene API theo SPEC. Cố định asset URLs và seed. GSAP timeline paused, frame(t) gọi seek(t); Three.js cập nhật camera/object từ t rồi render scene. Với R3F/Remotion dùng frame/fps cùng FilmData, không phụ thuộc vòng lặp realtime. Chọn 2D hoặc 3D theo nhu cầu, không bắt cả hai.

Kiểm tài sản tham chiếu tồn tại và source chạy được. Look/smoke/random seek chỉ khi chẩn đoán lỗi hoặc người dùng yêu cầu; không sinh vòng Visual PASS bắt buộc. Tắt placeholder khi nội dung thật hoàn thành. SKIPPED P15 có lý do nếu phim 2D.

## M5: timeline

OpenFilm film.html có track section và iframe/media với src tương đối, fragment `#t=in,out`, `at` là vị trí trên timeline. Duration đoạn được cắt phải khớp shot; offset thoại lấy từ FilmData. Caption overlay phải dùng cùng timeline. Chuyển cảnh/gain/color dùng khả năng đã xác minh, tránh ép API từ phiên bản khác.

Kiểm toàn bộ src, audio durations và shot boundaries bằng dữ liệu. External inputs dùng hash lúc duyệt; file do packet trước tạo dùng outputHashes thực ngay trước khi chạy packet sau. Bất kỳ input bị đổi ngoài scope thì dừng đúng phần bị ảnh hưởng và xác minh lại.

## M6–M7: render, bàn giao và sửa

Đọc CLI --help đã cài, giữ executable/cwd/options cụ thể. Ví dụ với CLI đã xác minh hỗ trợ: `openfilm render --out ABS_OUTPUT.mp4 --fps 24 --workers 1` trong thư mục film.html. Lưu argv/cwd/exitCode/stdout/stderr. Tránh ghi token/URL truy cập Studio vào gói chia sẻ; giữ log gốc cục bộ và bản đã che token cho bàn giao. Không coi exitCode=0 là đủ.

FFprobe kiểm codec, streams, FPS, resolution, duration. FFmpeg decode toàn MP4 và WAV để phát hiện hỏng/truncated. Video yêu cầu thoại phải có audio stream; silent profile ghi rõ requiresAudio=false. Hash output sau render. `finish_first.check_file` thực thi các kiểm tra file này; không đánh giá thẩm mỹ.

Ghi `video={path,sha256,version,requiresAudio,status:OUTPUT_READY}`, dùng DELIVER_VIDEO sau bàn giao. Gửi video/source/captions/manifest thật; không tự ghi USER_ACCEPTED. Phản hồi rõ targetIds/category/request tạo revisionPlan. Sao lưu hash và videoHistory trước sửa. Giữ nguyên nguồn cảnh không liên quan, tạo V02 chưa tồn tại, render và register_revision; kiểm lại SHA V01 trước bàn giao V02.

## Bộ mẫu tái lập bằng runtime có sẵn

`scripts/run_vieneu_gpu.py`: model+codec local, NVIDIA/PyTorch CUDA thật, WAV và GPU_EXECUTION.json. `scripts/build_production_sample.py`: bảy tài liệu mẫu, FilmData, storyboard, SVG/GSAP ba cảnh, VTT/SRT và hai thư mục version. Chỉ chạy khi user yêu cầu bài thử; không chạy khi chỉ đọc skill. Đọc tham số --help, dùng thư mục mới và GSAP có sẵn. TTS script từ chối overwrite và không tải model. Bài tone cũ chỉ là fixture runtime, không thay bằng chứng VieNeu hoặc phim đầy đủ.


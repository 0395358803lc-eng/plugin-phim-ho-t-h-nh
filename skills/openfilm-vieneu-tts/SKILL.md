---
name: openfilm-vieneu-tts
description: "Sử dụng khi phim hoạt hình cần giọng đọc, thuyết minh, hội thoại tiếng Việt bằng VieNeu-TTS cục bộ; kiểm tra tái sử dụng môi trường, tạo WAV và nghiệm thu audio trước khi đồng bộ với timeline OpenFilm."
---

# VieNeu-TTS → OpenFilm: lời thoại, giọng kể và thuyết minh tiếng Việt

## Vai trò và nguồn

Tên người dùng có thể viết "VietNeu-TTS"; tên chính thức là **VieNeu-TTS** (`pnnbao97/VieNeu-TTS`, Python `vieneu`). Năng lực: TTS tiếng Việt, giọng đọc preset, hội thoại đa nhân vật, v3 Turbo 48kHz và voice cloning khi được phép. Đây là **skill điều phối**, không đóng gói SDK/weights/model; không thể thực thi nếu máy chưa có runtime được cấp phép. **VieNeu-TTS v3 Turbo là nhánh open-source**; v4 là nhánh proprietary/API, không được tự thay thế hoặc mua dịch vụ.

Nguồn upstream và yêu cầu: `https://github.com/pnnbao97/VieNeu-TTS`, `README.md`, `pyproject.toml`, model v3 Turbo `https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo`. Tại thời điểm tham khảo upstream pyproject yêu cầu Python >=3.10 và bản SDK hỗ trợ GPU PyTorch CUDA (ưu tiên trên Windows) và CPU ONNX dự phòng, `uv sync` cho môi trường khóa phụ thuộc; hãy xác minh lại phiên bản/revision, checksum, license model và wheel theo máy trước khi chốt lệnh cài. Không giả định có sẵn model vì Python package đã cài.

## Giai đoạn 1: môi trường (bắt buộc trước khi viết vào Windows)

1. Theo `video-hoat-hinh` và `openfilm-moi-truong`: **P00 chọn/kiểm chứng máy → P01 hỏi PROJECT_DIR → P02 tạo/tái sử dụng VIDEO_HOAT_HINH_WORKSPACE → P03 tìm workspace cũ → P04 kiểm kê → P05 báo thiếu/xin duyệt**. Không nhảy qua P02 để cài ngay TTS.
2. Kiểm tra B04 VieNeu-TTS và T01–T07 (Python, uv nếu cần, SDK, model/cache, **PyTorch CUDA GPU là ưu tiên**; T06 GPU/driver/VRAM; T07 ONNX/CPU dự phòng khi được duyệt). Tìm GPU venv/torch CUDA và model cache trong workspace cũ trước. Nếu GPU không tương thích, thiếu VRAM hoặc test không đạt, chứng minh lý do rồi mới **đề xuất** CPU, không chuyển âm thầm.
3. Chưa phê duyệt cài/tải thì dừng tại báo cáo P05. **Không chạy lệnh `pip`, `uv sync`, `Vieneu()`, model init hoặc Web UI** trong kiểm kê: chúng có thể ghi cache hay tải file. Không thay OS, driver, CUDA Toolkit, PATH toàn hệ thống; không cài global.
4. Không tự yêu cầu Docker, remote API hay dịch vụ trả phí. Khi người dùng duyệt, cài trong `WORKSPACE/tools/vieneu` hoặc venv riêng được chốt, đưa model/cache ở vị trí được duyệt; kiểm tra hash/nguồn và nghiệm thu từng thành phần trước khi tạo audio.

## Giai đoạn 2: phân cảnh và chuẩn bị lời thoại

1. Từ storyboard/beat, tạo `dialogue_manifest.json` gồm `shot_id`, `character_id`, `script_original`, `script_spoken`, `voice_id`, `style_or_emotion`, `order`, `target_duration_s` (nếu được giao), và output path. Giữ nguyên `script_original`; mọi thay đổi phát âm/viết số đọc phải được ghi nhận và duyệt nếu thay nghĩa.
2. Chuẩn hóa tiếng Việt có kiểm tra: dấu câu, số/ngày/giờ/viết tắt/tên riêng, Việt-Anh; chia thành từng câu/nhịp ngắn để dễ sửa và đồng bộ. Không suy diễn phụ đề từ lời thoại chưa thực sự phát ra.
3. Ưu tiên **preset voices đã được xác minh** từ runtime với `list_preset_voices()` chỉ trong pha chạy đã được duyệt. Chọn giọng theo từng nhân vật, giữ nhất quán với cùng `voice_id`, ví dụ nam/nữ hoặc sắc thái phù hợp. Emotion cues như `[cười]` là thử nghiệm, phải nghe QC, không cam kết hiệu ứng chính xác.
4. Voice cloning/nhân bản giọng nói chỉ khi người dùng có **quyền sử dụng bản ghi và đồng ý rõ ràng của người sở hữu giọng**. Không clone giọng người thật không được phép, không mạo danh; giữ dữ liệu giọng riêng tư, không upload ra dịch vụ khác khi chưa được duyệt. Đối với nhân vật hư cấu ưu tiên giọng preset hoặc giọng có quyền.

## Giai đoạn 3: tổng hợp theo công việc đã duyệt

1. Mặc định chọn **GPU CUDA/PyTorch** khi VietNeu-TTS được bật. Ở P06 sau phê duyệt, xác minh GPU PyTorch và tạo WAV mẫu thật; SDK upstream dùng `from vieneu import Vieneu`, `tts = Vieneu(mode="v3turbo", backend="pytorch")` theo revision đã kiểm tra, `audio = tts.infer(text, voice=voice_id)`, `tts.save(audio, path)`; đây **không phải lệnh P04**. Nếu runtime ngầm chuyển CPU/ONNX, đánh dấu GPU FAIL/BLOCKED, không tự chấp nhận. Nếu GPU không đáp ứng, phải có hồ sơ `GPU_DECISION.json` + ID phê duyệt CPU mới được chọn `backend="onnx"`.
2. Chỉ dùng backend đã nghiệm thu trong `reports/tts/GPU_DECISION.json`: nếu `cuda-pytorch` phải có GPU smoke PASS; nếu `onnx-cpu` phải có bằng chứng GPU không đáp ứng và phê duyệt fallback. Tạo từng file WAV không ghi đè gốc trong `WORKSPACE/projects/<film-id>/assets/audio/voice/`; gắn mã `shot_id_character_id_take01.wav`. Lưu manifest JSON/CSV về voice, câu, phiên bản SDK/model, backend, tham số và thời gian thực tế; không ghi tokens/keys.
3. Nếu cần sửa lời thoại, chỉ render lại đoạn liên quan, không tạo lại tất cả. Giữ raw WAV chất lượng gốc, tránh nén lossy trước khi vào OpenFilm; chỉnh gain, giảm noise, thêm pause có ghi vào manifest. Không tự thay đổi kịch bản đã duyệt.
4. Dùng FFprobe đọc duration/channel/sample rate thực tế; trên v3 Turbo dự kiến 48 kHz theo upstream, nếu khác ghi đúng kết quả. Không có file/thông số từ máy thì không báo đã sinh audio.

## Giai đoạn 4: kết hợp OpenFilm và nghiệm thu

1. Chèn WAV làm `<audio>` track trong `film.html` qua asset path tương đối thuộc dự án; **không** phát audio từ `scenes/*.html` trong `window.film.frame(t)` (tránh lặp khi scrub/render). Điều chỉnh starts, transitions, shot durations theo WAV đã đo để đồng bộ chuyển cảnh/khẩu hình. Không ép voice thành một phần của timeline GSAP hoặc Remotion khi đã có audio nguồn.
2. SRT/VTT phải căn từ thời lượng/aligner thực và đối chiếu tai nghe hoặc waveform; không tạo timestamps chính xác giả từ số lượng ký tự. Dùng caption VTT ở track OpenFilm khi định dạng hỗ trợ.
3. QC theo mỗi đoạn: phát âm đúng dấu/tên riêng, không bỏ/thêm/lặp từ, nhịp đọc, khoảng im lặng, cân bằng âm lượng, peak/clipping, noise, tính nhất quán nhân vật, timing phụ đề và khớp hình. Báo `PASS/FAIL/BLOCKED` kèm file, logs, report, kết quả nghe thực tế.
4. Nếu Remote Desktop Commander không đưa âm thanh về ChatGPT, xuất **đoạn WAV/MP3 QC có thật** qua đường dẫn/link tải có thật để người dùng gửi vào chat, rồi mới đánh giá bằng cách nghe. Tuyệt đối không tuyên bố "đã nghe" chỉ dựa trên waveform hoặc log. Không công bố link tưởng tượng.
5. Chỉ sau QC đạt mới đưa vào mix cuối và xuất MP4 bằng OpenFilm. Quyền phê duyệt cài ID ≠ quyền tổng hợp giọng hoặc xuất phim; cần quyền rõ cho từng giai đoạn.

## Kết quả mỗi công việc

- Manifest câu và giọng / engine revision / WAV có thể kiểm tra / FFprobe duration & sample rate / VTT nếu có align / bảng QC từng câu / trạng thái phê duyệt. Nếu bị BLOCKED do thiếu model, chưa có consent, hoặc chưa nghe được, trả kết quả hiện có và yêu cầu bước hợp lệ; không suy đoán.

Xem `references/INTEGRATION.md`, `references/GPU_FIRST_POLICY.md` và `openfilm-moi-truong/references/VIENEU-TTS-WINDOWS.md`.

## Cập nhật luồng âm thanh nếu Remotion Master (N10–N12)

Đầu ra VieNeu vẫn là từng WAV đã nghe/FFprobe, script nguyên gốc và spoken text được lưu. Chọn master tại `openfilm-hybrid-master`: OpenFilm Master import WAV vào `<audio>` track `film.html`; Remotion Master giữ WAV trong `remotion/public/audio/` và tạo `Sequence`/`Audio` theo `FilmData` integer frames. Không render/nhập cùng lời thoại hai lần, không bịa chính xác word-level align. Cập nhật shot/endFrame theo WAV duration đo thực (không dựa trên số ký tự), có phê duyệt khi phải thay thời gian đã khóa. Xem `openfilm-audio-subtitles` để kiểm font Việt, SRT/VTT và ducking.

## Khóa nguồn TTS v1.8.0

Trước P12 tổng hợp câu nào, **P08.05 hoặc P12.08** phải có `reports/tts/VOICE_SOURCE_LOCK.json` hợp lệ theo `references/validate_voice_source_lock.py`. Mặc định `source=vieneu-local`, `backend=cuda-pytorch`; GPU runtime phải PASS theo `GPU_DECISION.json` và T06 trước khi sinh audio. Nếu CPU fallback đã được duyệt riêng T07 mới có thể `backend=onnx-cpu`. `openfilm get voice`, `openfilm canvas tts` và Studio provider TTS khác bị từ chối theo policy; không được tự gọi dù upstream OpenFilm hướng dẫn. Provider thay thế là một **thay đổi phạm vi cần duyệt riêng**, không phải silent fallback. Khóa ghi path theo workspace và lời thoại; sau đó import WAV vào OpenFilm; không phát audio hai lần.

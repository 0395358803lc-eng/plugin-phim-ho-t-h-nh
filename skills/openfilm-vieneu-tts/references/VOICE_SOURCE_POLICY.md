# Khóa nguồn TTS VieNeu local — P08.05 / P12.08 (v1.8.0)

Khi dự án dùng VieNeu-TTS, chỉ **một nguồn âm thanh thoại đã duyệt** được phép vào master. Tạo `reports/tts/VOICE_SOURCE_LOCK.json` sau P08.05 với `source=vieneu-local`, `backend=cuda-pytorch`, `modelRevision` đã kiểm, `voicePresetIds` đã được người dùng đồng ý, `gpuDecisionPath`, `origin=WAV_LOCAL`, và `openFilmTtsAllowed=false`. Nếu không có lời thoại, `source=none`, `backend=none`. CPU fallback chỉ sau GPU không đáp ứng + approve T07 ghi trong GPU_DECISION.json và voice lock tương ứng.

**Lệnh bị chặn khi khóa VieNeu:** `openfilm get voice`, OpenFilm Canvas `tts` node/Make node, Studio voice-over provider, plugin/cloud TTS và các lệnh có thể phát sinh phí khi không có phê duyệt. **Chỉ import WAV từ VieNeu** được kiểm bằng FFprobe và nghe QC; hai track master không cùng phát một lời thoại. `openfilm get music/sfx` không phải TTS nhưng vẫn cần quyền media/provider/license/chi phí riêng.

Nếu người dùng yêu cầu nhà cung cấp TTS khác, tạo phương án và **phê duyệt riêng** mô tả service, privacy, license, cost, phạm vi, trước khi đổi `source=alternate-approved`; không coi v1.8.0 tự cho phép gọi dịch vụ mới. Dự án vẫn không dùng TTS ở OpenFilm khi chưa có `allowOpenFilmProvider=true` đi kèm `alternateProviderApprovalId` hợp lệ. **Không tự động chuyển nguồn khi ViveNeu GPU lỗi.**

Validator `validate_voice_source_lock.py` (stdlib) kiểm các field, backend, approval và tính nhất quán với GPU decision JSON nếu được truyền; nó không xác minh thực sự người dùng đã click, backend runtime hoặc WAV. Tất cả evidence phải nằm trong workspace và được đọc lại từ file thực.

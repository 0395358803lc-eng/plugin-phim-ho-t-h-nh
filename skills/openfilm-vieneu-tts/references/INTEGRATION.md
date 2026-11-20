> v1.14.0: FINISH_FIRST_USER_REVIEW ưu tiên. Đây là công thức kỹ thuật/tham khảo; mọi đánh giá thẩm mỹ chỉ theo yêu cầu người dùng, mọi cổng QC legacy không chặn V01. OpenFilm CLI-first, GUI tùy chọn.

# VieNeu-TTS ↔ OpenFilm · contract và checklist ứng dụng

## Contract file trung gian

```text
VIDEO_HOAT_HINH_WORKSPACE/
  tools/                  # Python venv/SDK, CHỈ khi được duyệt cài
  cache/                  # HF model cache theo path được duyệt (GPU-first, ONNX chỉ fallback)
  projects/<film-id>/
    film.html
    scenes/
    assets/audio/voice/  # WAV đã duyệt, giữ đường dẫn tương đối
    captions/            # WebVTT/SRT kiểm chứng bằng timing thực
  qc/tts/                 # log, FFprobe metadata, mẫu nghe
  reports/               # manifest nguồn, version, license/consent (không có secret)
```

Ví dụ manifest một câu (không phải đầu ra đã render):

```json
{
  "shot_id": "shot-001",
  "character_id": "narrator",
  "script_original": "Chào các bạn!",
  "script_spoken": "Chào các bạn!",
  "voice_id": "preset đã xác minh",
  "engine": "vieneu / v3 Turbo (xác minh runtime)",
  "backend": "cuda-pytorch (PENDING_GPU_QC)",
  "wav_path": "assets/audio/voice/shot-001_narrator_take01.wav",
  "duration_s": null,
  "qc_status": "PENDING"
}
```

`duration_s=null` cho đến khi FFprobe xác minh. Với một phiên bản SDK đã được duyệt và đã có model local, mẫu API upstream là:

```python
from vieneu import Vieneu
engine = Vieneu(mode="v3turbo", backend="pytorch")  # GPU first; có thể tải model; KHÔNG chạy trong P03–P05
voices = engine.list_preset_voices()
# Chọn voice_id hợp lệ từ voices theo phê duyệt của người dùng.
# audio = engine.infer(script_spoken, voice=voice_id)
# engine.save(audio, output_wav)
```

Để PASS GPU phải kiểm `torch.cuda.is_available()` và nhận diện backend/device PyTorch CUDA thực tế + có WAV smoke; không chỉ dựa vào tên GPU. Chỉ dùng ONNX CPU khi file `GPU_DECISION.json` ghi bằng chứng GPU không đáp ứng và ID phê duyệt fallback. Không tự chạy code trên nếu chưa được phê duyệt cài/tải model và tạo audio; kiểm tra API theo SDK đã cài. Sau tổng hợp, kiểm tra mẫu và gắn đường dẫn WAV tương đối vào audio track của `film.html`; không kích hoạt audio bên trong `window.film.frame(t)`. Chỉ tạo VTT/SRT với timestamps có nguồn từ alignment thực và nghe xác nhận; không suy từ số chữ.

## Chuẩn nghiệm thu TTS

| Cổng | Bằng chứng | Điều kiện đạt |
| --- | --- | --- |
| TTS-ENV | Python/SDK/model/cache/backend, GPU VRAM/driver, torch CUDA, revision, license, đường dẫn | **CUDA GPU/PyTorch + smoke PASS**; hoặc CPU fallback có evidence GPU thất bại và phê duyệt mới |
| TTS-SCRIPT | Script gốc + script_spoken, nhân vật, nhãn giọng | Không đổi nghĩa; phân vai có duyệt |
| TTS-WAV | WAV, duration, sample_rate/channel/peak và FFprobe | Có file và không clipping bất thường |
| TTS-LISTEN | Mẫu nghe, nhận xét phát âm/prosody/ngắt câu | Đã thực sự nghe hoặc BLOCKED |
| TTS-SYNC | Timeline OpenFilm, cue VTT/SRT, điểm đầu-cuối shot | Theo audio đo thực tế, không giả timestamp |
| TTS-PUBLISH | MP4 đã render và nghe lại audio tổng | Chỉ PASS khi file cuối kiểm chứng |

## Các nguồn chính thức

- https://github.com/pnnbao97/VieNeu-TTS
- https://github.com/pnnbao97/VieNeu-TTS/blob/main/README.md
- https://github.com/pnnbao97/VieNeu-TTS/blob/main/pyproject.toml

Không đưa proprietary API v4, model checkpoint hay voice reference được cấp quyền vào plugin ZIP. Đây là tài liệu điều phối, không có quyền thực thi model tự thân.

> v1.14.0: FINISH_FIRST_USER_REVIEW ưu tiên. Đây là công thức kỹ thuật/tham khảo; mọi đánh giá thẩm mỹ chỉ theo yêu cầu người dùng, mọi cổng QC legacy không chặn V01. OpenFilm CLI-first, GUI tùy chọn.

# VieNeu-TTS Windows — GPU-first audit, cài đặt và CPU fallback có phê duyệt (v1.7.0)

Đây là hướng dẫn kỹ năng; **không phải bằng chứng máy đã được kiểm tra hoặc TTS chạy được**. User yêu cầu GPU là lựa chọn mặc định khi bật VieNeu-TTS. Ưu tiên VieNeu-TTS **v3 Turbo open-source** (thường xuất WAV 48 kHz), SDK `vieneu` của `pnnbao97/VieNeu-TTS`, không tự chuyển sang v4 proprietary. Mọi lệnh cài là **mẫu kế hoạch chờ duyệt**, tuyệt đối không chạy trong P03–P05.

## Quyết định bắt buộc: ưu tiên CUDA/GPU trước

1. `GPU_CANDIDATE`: Windows có NVIDIA GPU, driver/capability có triển vọng hỗ trợ PyTorch CUDA; xác minh phiên bản Python, VRAM tổng/còn trống, driver CUDA version, nguồn wheel. Ở P04 chỉ dùng metadata read-only, *chưa* được kết luận GPU hoạt động.
2. `GPU_NOT_READY_PACKAGE`: GPU có nhưng thiếu torch CUDA/torchaudio/transformers/SDK/model; lập kế hoạch T03–T05 để cài cục bộ sau phê duyệt, **không** thay bằng CPU vì thiếu package.
3. `GPU_UNSUPPORTED`: không có CUDA NVIDIA tương thích với backend GPU dự kiến hoặc phần cứng/driver hỗ trợ không phù hợp (có bằng chứng). Chỉ **đề xuất** T07 CPU cho user, chưa tự cài.
4. `GPU_INSUFFICIENT`: VRAM/tài nguyên không đáp ứng tác vụ sau khi đánh giá cách giảm batch, tuần tự hóa TTS tránh render/WebGL cạnh tranh (có bằng chứng). Trình giải pháp GPU trước; nếu không khả thi mới trình CPU T07.
5. `GPU_FAILED`: khi đã được duyệt thử runtime P06 nhưng `torch.cuda.is_available()` false, device mismatch, CUDA OOM/driver error, hoặc WAV không thể tạo trên GPU; ghi logs và đề xuất sửa GPU trong phạm vi được duyệt. Chỉ trình CPU khi GPU không đáp ứng sau chẩn đoán, không tự fallback.
6. `GPU_RUNTIME_PASS`: chỉ sau P06 đã được duyệt, test runtime thật: `torch.version.cuda`, `torch.cuda.is_available()`, device ID/name, `Vieneu(mode="v3turbo", backend="pytorch")` **theo API phiên bản kiểm chứng**; tạo một WAV thử từ preset có quyền, FFprobe metadata và kiểm nghe. Không chấp nhận việc SDK tự chuyển CPU mà không báo.

Không lấy GPU yêu cầu cho render video thay thế việc kiểm tra GPU TTS. Không đưa ra con số VRAM tối thiểu chung không có căn cứ; dùng model thật, batch, dữ liệu test và độ trống thực tế. CUDA Toolkit không mặc nhiên phải cài nếu wheel torch CUDA đã mang runtime tương ứng, **không** tự đổi driver/OS/toolkit.

## P03 — Tìm môi trường GPU cũ trước

Trong các workspace cũ đã được user cho phép: kiểm `tools/vieneu`, `.venv`, `uv.lock`, `dist-info`, torch/torchaudio CUDA wheel và `vieneu`, `transformers`, cache model revision, dung lượng và đường dẫn liên quan. Chỉ REUSE_OK khi có nguồn, architecture, version, path, phụ thuộc phù hợp; PyTorch CPU-only **không được gọi là GPU_READY**, venv cũ có thể không portable. Không tự sao chép cache/model, link junction hoặc đọc token.

## P04 — Kiểm tra CHỈ ĐỌC

- Windows GPU/vendor: `Get-CimInstance Win32_VideoController` hoặc metadata tương đương (nếu được phép).
- NVIDIA nếu có: `nvidia-smi --query-gpu=name,driver_version,memory.total,memory.free,compute_cap --format=csv,noheader` khi lệnh hỗ trợ; lỗi query field -> thử read-only query đơn giản, ghi `UNVERIFIED`, không giả kết quả.
- Xác minh Python (theo upstream Python>=3.10 nhưng kiểm wheel Windows **của phiên bản chính xác**), `pip`/`uv` từ metadata, torch CUDA wheel, torchaudio, transformers, SDK và cache model. Không gọi `Vieneu()`, không tải/sync/install, không chạy inference/Web UI ở P04. Không giả `GPU_RUNTIME_PASS` từ `nvidia-smi`.

## P05 — ID cài đặt có điều kiện và yêu cầu phê duyệt

| ID | Vai trò | Chính sách |
|---|---|---|
| B04 | VieNeu-TTS | Tính năng có giọng Việt đã được người dùng chọn |
| T01 | Python phù hợp | Venv dưới `WORKSPACE/tools` hoặc dùng lại bản hợp lệ |
| T02 | uv hoặc pip quản lý riêng | Tùy phương án cài đã duyệt, không global |
| T03 | SDK `vieneu` | Cần cho GPU và CPU, không dùng `pip install vieneu` để kết luận GPU đã có |
| T04 | Model/cache VieNeu-TTS v3 Turbo | Revision, license, SHA256 nếu có, dung lượng, nguồn chính thức, không download trước duyệt |
| T05 | **PyTorch CUDA + torchaudio + transformers** | **Đường cài ưu tiên** cho Windows GPU, kiểm wheel CUDA/driver/Python và pin version |
| T06 | **GPU/VRAM/driver/CUDA preflight** | Gate read-only, không phải hạng mục tải; không tự sửa driver |
| T07 | ONNX/CPU fallback | Chỉ trình đề xuất khi GPU không hỗ trợ/không đủ/không chạy được, kèm chứng cứ và approval ID mới |

Ví dụ lệnh upstream GPU cho **kế hoạch** (chỉ dùng sau khi user phê duyệt, đã kiểm thích hợp và khóa wheel/hash):

```powershell
# Minh họa của upstream, KHÔNG tự chạy ở P03–P05:
python -m pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128
python -m pip install "transformers==4.57.6"
python -m pip install vieneu
# Hoặc nếu dùng repo + uv, xác minh `uv sync --extra cuda` theo pyproject/lockfile đúng revision.
```

Bản pin trên chỉ là ví dụ tài liệu upstream tại thời điểm tham khảo, **không phải bảo đảm hỗ trợ mọi GPU/Python/Windows**. Không dùng các lệnh `irm ... | iex` tự động, `@latest`, installer global hoặc sửa `PATH`, driver, OS. Nếu không tìm thấy wheel tương thích hay dung lượng/checksum xác minh được, báo `CHƯA XÁC MINH` và dừng tại P05.

## P06 / P12 — Nghiệm thu thực và chặn CPU fallback âm thầm

Sau khi user duyệt cài/test (phê duyệt đặc biệt khi cần): thực hiện liên tiếp hai checklist kỹ thuật nội bộ trong macro M0 — xác minh CUDA PyTorch thật và tổng hợp WAV ngắn trên GPU; lưu `reports/tts/GPU_DECISION.json`, `qc/tts/gpu-smoke.wav`, logs, FFprobe và điều kiện đạt. Mẫu khởi tạo chỉ sau duyệt:

```python
import torch
assert torch.cuda.is_available(), "GPU CUDA chưa sẵn sàng — BLOCKED"
from vieneu import Vieneu
engine = Vieneu(mode="v3turbo", backend="pytorch")  # xác minh keyword theo SDK phiên bản đang dùng
# Chọn preset voice hợp lệ rồi tạo WAV kiểm thử, KHÔNG gọi trong P03–P05
```

Cần xác nhận engine/backend thực là `pytorch/cuda`, device không phải CPU; `torch` import thành công **không** là nghiệm thu. Test phải giữ file WAV có thể mở và kiểm metadata; nghe thực sự hoặc `BLOCKED` cho kiểm nghe. P12 chỉ sinh WAV production bằng backend đã PASS, ghi mỗi `voice-manifest.json` backend/device/version và đường dẫn. Nếu có lỗi GPU, lưu nguyên trạng và trình nút **Phê duyệt sửa GPU**; chỉ có nút **Phê duyệt CPU dự phòng** khi đã chứng minh GPU không đáp ứng và đề xuất CPU cụ thể. Khi CPU được duyệt mới chạy ONNX, không đổi engine tự động, không thay model/giọng hoặc chất lượng khi chưa kiểm chứng. Kiểm quyết định bằng `openfilm-vieneu-tts/references/validate_gpu_decision.py` (stdlib; chỉ đọc).

Nguồn kiểm chứng cần đối chiếu tại lúc triển khai: https://github.com/pnnbao97/VieNeu-TTS/blob/main/README.md ; https://github.com/pnnbao97/VieNeu-TTS/blob/main/pyproject.toml ; https://pytorch.org/get-started/locally/ .

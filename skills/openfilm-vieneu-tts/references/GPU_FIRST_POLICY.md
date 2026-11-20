# VieNeu-TTS GPU-first — quyết định backend và nghiệm thu (v1.7.0)

**Nguyên tắc không thương lượng:** Khi người dùng chọn VieNeu-TTS, GPU/PyTorch-CUDA là đích cài và vận hành mặc định trên máy Windows. Nếu GPU không sẵn sàng, **chưa tự chuyển CPU**. CPU/ONNX chỉ được **đề xuất** sau khi có bằng chứng GPU không đáp ứng và chỉ chạy khi user duyệt một lần riêng đúng ID. Phê duyệt nâng cấp plugin không phải quyền cài phần mềm. Nếu không bật VieNeu-TTS, không yêu cầu cài GPU TTS.

## Thứ tự và quyết định

`P00 CONNECT` → `P01 PROJECT` → `P02 WORKSPACE` → `P03 REUSE GPU VENV/MODEL` → `P04 GPU READONLY AUDIT` → `P05 GPU INSTALL PLAN` → `STOP APPROVAL` → `P06 INSTALL GPU ID+TEST GPU WAV (nếu duyệt)` → `P12 PRODUCE CUDA WAV`. Điều kiện không có NVIDIA CUDA / GPU test FAIL / VRAM không đáp ứng → `GPU_NOT_READY`, ghi bằng chứng; đề xuất giải pháp GPU hợp lý trước, nếu không khả thi mới xin duyệt `T07 CPU/ONNX`. Cấm cài CPU mặc định và cấm SDK silent-fallback.

| Điều kiện | Quyết định | Có thể làm gì? |
|---|---|---|
| NVIDIA GPU tương thích; thiếu torch CUDA | `GPU_CANDIDATE` | P05 lập kế hoạch T05 CUDA; không chọn CPU |
| T05 có sẵn, chưa chạy test | `GPU_CANDIDATE` | P06 xin phép CUDA smoke; chưa gọi READY |
| GPU WAV smoke thành công, device đúng | `GPU_RUNTIME_PASS` | Cho phép P12 sử dụng CUDA và ghi metadata |
| GPU không có hoặc không tương thích | `GPU_UNSUPPORTED` | Đề xuất T07 ONNX CPU với bằng chứng, chờ user duyệt |
| VRAM thiếu sau các cách batch nhỏ, tách render | `GPU_INSUFFICIENT` | Đề xuất T07 với bằng chứng, chờ user duyệt |
| Runtime GPU lỗi sau thử/phân tích được phép | `GPU_FAILED` | Trình phương án sửa GPU; chỉ sau đó đề xuất CPU có duyệt |
| Chưa đủ dữ liệu GPU | `NOT_VERIFIED` | Dừng, kiểm tra thêm metadata, không cài CPU |

## Quy trình cài/kiểm tra và báo cáo

- `T01`: Python phiên bản tương thích wheel GPU Windows; `T02`: uv/pip cục bộ; `T03`: SDK `vieneu`; `T04`: model/cache; `T05`: torch CUDA + torchaudio + transformers; `T06`: GPU/VRAM/driver read-only; `T07`: ONNX CPU chỉ fallback. Trình SHA256, URL chính thức, phiên bản pin, size khi có căn cứ; không bịa dữ liệu còn thiếu.
- P04 **không chạy** `Vieneu()`, `pip install`, `uv sync`, `snapshot_download`, model init, CUDA smoke. Ở P06 sau approve `torch.cuda.is_available()`, `torch.version.cuda`, device, CUDA capability, GPU VRAM; tạo WAV preset ngắn thực có phép, đo ffprobe; cần nghiệm thu nghe. Không có nghe thì QC nghe `BLOCKED` dù metadata PASS.
- P12 `selectedBackend == cuda-pytorch` phải có bằng chứng GPU smoke PASS; audio metadata phải ghi `backend`, `gpuName`, `cudaRuntime`, `torchVersion`, `modelRevision`, `wavPath`, `duration` đo thật. Nếu `selectedBackend == onnx-cpu`, bắt buộc `cpuFallbackApprovalId` và `gpuEvidencePaths`. Không bắt buộc CPU chỉ vì GPU kém nhanh ở câu ngắn: đây là ưu tiên của user.
- Mẫu state: `reports/tts/GPU_DECISION.json` (xem `GPU_DECISION_TEMPLATE.json`) có `ttsRequired`, `desiredBackend`, `selectedBackend`, `gpuAssessment`, `gpuEvidencePaths`, `runtimeGpuWavEvidence`, `cpuFallbackApprovalId`. Chạy `validate_gpu_decision.py` không ghi file. Đánh giá sự thật từ log/files runtime, không dựa vào template JSON.
- CPU fallback là **phương án thay đổi cần phê duyệt riêng**, không mặc định được phép chỉ vì duyệt P05/T05; nếu user từ chối CPU, trạng thái `BLOCKED`, không làm P12.

Tài liệu upstream cần kiểm tra revision: https://github.com/pnnbao97/VieNeu-TTS/blob/main/README.md ; https://github.com/pnnbao97/VieNeu-TTS/blob/main/pyproject.toml ; https://pytorch.org/get-started/locally/ . Ví dụ Windows từ upstream có PyTorch CUDA wheels, không ngụ ý cài CUDA Toolkit/driver global là cần thiết.

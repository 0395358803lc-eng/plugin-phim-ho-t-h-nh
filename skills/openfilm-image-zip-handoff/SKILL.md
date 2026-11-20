---
name: openfilm-image-zip-handoff
description: "Use when ChatGPT creates any image for a Video-hoạt-hình project and the user's images must be delivered to a Windows workspace by downloadable ZIP; also when a visual QC gate is BLOCKED because ChatGPT-produced PNGs cannot be written to the remote computer."
---

# Video-hoạt-hình — tạo ảnh → ZIP tải về → người dùng đặt vào workspace (v1.13)

**BẮT BUỘC** cho các lượt tạo ảnh thực được người dùng phê duyệt trong dự án, bao gồm storyboard P10.05, nhân vật/asset P11, look preview và ảnh khung hình khác do ChatGPT sinh khi phù hợp. Dùng khi đầu ra image_gen chỉ nằm trong chat và **không có đường truyền nhị phân đã được phê duyệt** để chuyển thẳng vào máy Windows. Đường bàn giao ZIP là giải pháp chính, không được tự đổi sang lệnh upload/PowerShell/remote Python không nằm trong quyền người dùng.

## Cam kết hai bước, không đánh tráo bằng chứng

1. **ChatGPT tạo ảnh và phát hành ZIP** (nếu image bytes thật có trong môi trường hiện tại) → trạng thái `ZIP_READY_FOR_DOWNLOAD`, `AWAITING_USER_EXTRACTION`. ZIP chứng minh **ảnh có trong ZIP chat**, không chứng minh PNG đã nằm trong remote workspace và **không** đủ cho `VISUAL_PASS`.
2. **Người dùng tải ZIP và giải nén vào thư mục được chỉ định** → ChatGPT xác minh trên đúng máy Windows đã duyệt: đọc lại đúng các PNG theo path, SHA256, kích thước và thực sự thấy pixel qua công cụ multimodal hoặc người dùng upload. Chỉ sau khi đã thấy ảnh mới được ghi image receipt, observation và đánh giá thị giác. Không tự nghiệm thu M2 hay mở scope ảnh khác.

## Mặc định tự động sau khi có quyền tạo ảnh

- Không chờ người dùng yêu cầu “tạo ZIP” lần nữa: nếu ảnh được tạo theo phê duyệt hiện hành, sau khi có PNG file-backed, **đóng gói ZIP và đưa link tải trong cùng lượt**. Không tự mở rộng từ 3 shot thành 25 shot. Lựa chọn tạo ảnh phải có căn cứ từ yêu cầu/cổng duyệt; chỉ hướng dẫn/kiểm thử plugin **không** kích hoạt sinh ảnh mới.
- Xác nhận `deviceId`, `workspace`, filmId và danh sách `targetId`/`targetRelativePath` đã được người dùng duyệt. Nếu chưa biết workspace, không bịa. Đường dẫn ví dụ của dự án hiện hành là `D:\phim-hoạt-hình\VIDEO_HOAT_HINH_WORKSPACE`; dự án khác dùng đúng workspace đã được chọn.
- Sinh ảnh bằng công cụ tạo ảnh được host cung cấp (khi hợp lệ). Kiểm tra image output có **đường dẫn PNG thật** trong môi trường thực thi hiện hành (`/mnt/data/...` hoặc đường dẫn được tool xác nhận). Nếu chỉ có ảnh hiển thị trong hội thoại mà không có file bytes truy cập được, **KHÔNG** tạo ZIP placeholder hay file ảnh giả. Dừng với `IMAGE_BINARY_UNAVAILABLE`, yêu cầu người dùng tải ảnh chat rồi tải lên lại nếu cần. Tuyệt đối không tự tạo ảnh trống, crop screenshot từ UI hay chế byte từ text.
- Dùng đúng ID bất biến `SHOT-SC001-01` v.v. Tên file cho output phải là `SHOT-...png`, không ghi đè file cũ. Mỗi lần tạo mới dùng `handoffId` khác, ví dụ `M2_P10_PILOT_SC001_SC009_SC012_20261120`.

## Đóng gói có chứng cứ trong ChatGPT

Đọc script hỗ trợ `references/image_handoff.py` và dùng Python stdlib có sẵn trong **môi trường ChatGPT**, không phải lệnh chạy trên Windows remote. Cung cấp một JSON spec có dạng:

```json
{
  "handoffId": "M2_P10_PILOT_SC001_SC009_SC012_20261120",
  "targetWorkspace": "D:\\phim-hoạt-hình\\VIDEO_HOAT_HINH_WORKSPACE",
  "images": [
    {
      "targetId": "SHOT-SC001-01",
      "inputPng": "/mnt/data/actual_image_generated_this_turn.png",
      "targetRelativePath": "projects/dua-con-hieu-thao-nhat-tren-mang/storyboard/previews/SHOT-SC001-01.png",
      "sourceTextPath": "projects/dua-con-hieu-thao-nhat-tren-mang/storyboard/shots/SHOT-SC001-01.md",
      "sourceTextSha256": "<verified-sha256-from-current-checkpoint>"
    }
  ]
}
```

Trên dữ liệu thật, điền SHA256 đã được kiểm (không dùng placeholder). Chạy:

```sh
python image_handoff.py pack --spec /mnt/data/vhh_handoff_spec.json --output /mnt/data/VHH_M2_P10_PILOT_SC001_SC009_SC012.zip
```

- ZIP chứa đúng PNG theo **đường dẫn tương đối từ workspace root**: `projects/<film>/storyboard/previews/<SHOT>.png`, plus `handoffs/<handoffId>/MANIFEST.json` (SHA256, kích thước, image ID) và `handoffs/<handoffId>/HUONG_DAN_GIAI_NEN.txt`. ZIP **không** chứa đường dẫn tuyệt đối, `..`, symlink, file model, tệp kịch bản nguồn hoặc các file ngoài scope.
- Script phải đọc lại ZIP và xác nhận toàn bộ entry và SHA256. Nêu rõ tổng số ảnh, mã ZIP SHA256, path đích. Xuất liên kết Markdown `[Tải ZIP ảnh](sandbox:/mnt/data/<exact-created-name>.zip)` **chỉ khi file thật vừa được tạo/đã xác minh trong container cùng lượt**. Không tự chế link `sandbox:` từ tên ảnh xuất hiện trong chat.
- Hướng dẫn: người dùng tải ZIP, giải nén **nội dung** vào thư mục gốc chính xác `D:\phim-hoạt-hình\VIDEO_HOAT_HINH_WORKSPACE` (không giải nén thêm một lớp tên ZIP); tránh ghi đè file PNG đã có trừ khi có quyền. Giải thích ảnh sẽ nằm tại `...\projects\<film>\storyboard\previews\...png`. Không yêu cầu chạy command hay cài app trên Windows chỉ để giải nén.

## Kiểm chứng sau khi người dùng đặt ZIP

1. Đợi người dùng xác nhận “đã giải nén” (hoặc tự thấy bytes file qua connector nếu được duyệt). Không tự đánh dấu `VISUAL_PASS` khi vừa cung cấp ZIP.
2. Xác minh đúng thiết bị/workspace, manifest tại `handoffs/<handoffId>/MANIFEST.json` và từng ảnh. Nếu đã được user cấp quyền **đọc**/chạy verifier offline, dùng script stdlib: `python image_handoff.py verify --workspace <workspace> --manifest handoffs/<handoffId>/MANIFEST.json`; nếu lệnh chưa được cho phép, đọc file + Get-FileHash qua những công cụ/lệnh đã duyệt, hoặc xin bổ sung đúng lệnh. Hash PNG phải trùng manifest.
3. **Thực sự đọc ảnh** bằng Remote Desktop Commander `read_file`/`read_multiple_files` chuyển `image` content tới ChatGPT, hoặc nhờ người dùng upload ảnh PNG vào chat. Mô tả từng ảnh cụ thể, ghi lỗi/khác nguồn, không sao chép OCR/bảng QC vẽ bên trong ảnh như bằng chứng thật.
4. Với P10.05, xét riêng SC001, SC009 và SC012; giữ cổng full M2/P11 đóng. Nếu ảnh SC012 vẫn có điện thoại trên bàn thay vì úp ở kệ xa bàn, phải ghi **FAIL** hoặc yêu cầu sửa trước QC.
5. `VISUAL_PASS` chỉ nếu nhận ảnh pixel thực, SHA đúng, đúng scene, đủ các required targets, QC không có blocker và có user approval ở cổng phù hợp. Có ảnh ZIP không đồng nghĩa đã thấy pixel remote, có checksum không đồng nghĩa đẹp/đúng bố cục.

## Phân loại trạng thái chuẩn

| Điều kiện | Trạng thái | Được tuyên bố gì |
|---|---|---|
| Ảnh chỉ hiển thị trong chat; không có file bytes | `IMAGE_BINARY_UNAVAILABLE` / `VISUAL_BLOCKED` | Không có ZIP thật |
| Tạo và xác thực ZIP, chưa có xác nhận giải nén | `ZIP_READY_FOR_DOWNLOAD` / `AWAITING_USER_EXTRACTION` | Có file ZIP tải được, **chưa** có PNG remote |
| Người dùng nói đã giải nén, chưa kiểm hash | `AWAITING_REMOTE_VERIFICATION` | Chưa có PNG/hash chứng thực |
| PNG hash đã đối chiếu, chưa thực sự xem ảnh | `AWAITING_VISUAL_INSPECTION` | File hợp lệ, chưa QC thị giác |
| Đã đọc ảnh thật, nhưng có lỗi continuity | `VISUAL_FAIL` | Cần sửa trong scope được duyệt |
| Đã đọc ảnh thật, kiểm từng target và đủ biên bản | `VISUAL_PASS` chỉ cho target đã duyệt | Không tự suy ra macro M2 PASS |

## Mẫu phản hồi user khi phát ZIP

“Đã tạo ZIP gồm N PNG thật và manifest. Tải [ZIP] (liên kết từ tệp đã xác minh), giải nén vào thư mục **[workspace root đã duyệt]**. Ví dụ ảnh đầu tiên sẽ nằm tại **[đường dẫn tuyệt đối]**. Sau khi giải nén, nhắn ‘đã đặt ảnh’; tôi sẽ kiểm SHA256 và xem lại ảnh. Hiện QC thị giác vẫn **CHỜ** — không phải PASS.”

**Không được:** giả tên file hoặc sandbox link; coi HTML/screenshot hoặc chữ `VISUAL_PASS` do ảnh sinh ra là QC; dùng PowerShell/Python remote không nằm trong `allowedCommands`; tự tải/cài chương trình; chép các ảnh sang source script; tự đánh dấu approval/M2 acceptance, thay master, hoặc mở rộng danh sách shot.

**Liên quan:** `openfilm-visual-inspection` (cổng multimodal); `openfilm-macro-bundles` (quyền macro và checkpoint); `openfilm-oneclick-approval` (tạo nút phê duyệt riêng cho phần làm mới nếu cần).

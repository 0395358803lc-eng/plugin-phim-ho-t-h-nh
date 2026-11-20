---
name: openfilm-image-zip-handoff
description: "Đóng gói PNG thật thành ZIP, chuyển đúng workspace và xác minh bytes/hash sau giải nén."
---

# Image ZIP handoff — v1.14.1

Dùng khi ảnh tạo trong chat cần đưa vào workspace và chưa có đường truyền bytes trực tiếp trong phạm vi đã cấp. Nếu đã có file thật trên cùng máy thì dùng trực tiếp; không tạo vòng tải/giải nén không cần thiết. Không sinh ảnh mới chỉ vì đang kiểm thử hoặc sửa plugin.

## Chuẩn bị dữ liệu thật

Xác nhận deviceId, workspace, filmId và targetIds từ tác vụ hiện hành. Mỗi ảnh có inputPng thực đọc được, targetRelativePath trong workspace, sourceTextPath và sourceTextSha256 đã tính từ nguồn. PNG chỉ hiện trong hội thoại mà không có bytes truy cập được là IMAGE_BINARY_UNAVAILABLE; không chế file rỗng, dùng screenshot UI thay ảnh hay đặt sandbox link giả.

Đọc [image_handoff.py](references/image_handoff.py). JSON spec có handoffId, targetWorkspace và images[]. Mỗi images[] có targetId, inputPng, targetRelativePath, sourceTextPath, sourceTextSha256. Ví dụ đường đích: `projects/film-a/assets/CHAR-MAM.png`; đây là minh họa, phải thay bằng ID/path/source hash thật. Không hard-code shot hoặc workspace của dự án khác.

## Đóng gói và bàn giao

Sau khi có quyền tạo ảnh và PNG thật, tự đóng ZIP trong cùng lượt; không hỏi thêm chỉ để đóng gói. Dùng executable/script có sẵn:

```text
python image_handoff.py pack --spec handoff-spec.json --output images-handoff.zip
python image_handoff.py verify --workspace WORKSPACE --manifest handoffs/HANDOFF_ID/MANIFEST.json
```

Lệnh pack chạy nơi có bytes nguồn. ZIP chứa PNG theo đường dẫn tương đối, `handoffs/<handoffId>/MANIFEST.json` và hướng dẫn giải nén. Không thêm model, nguồn kịch bản hoặc file ngoài scope. Đọc lại ZIP để đối chiếu entry, SHA256 và kích thước; chặn absolute path, .., symlink, trùng tên xung đột hoặc file ghi đè chưa được phép.

Bàn giao link trỏ file thực trong môi trường hiện hành, số ảnh, SHA256 ZIP và root đích đã xác minh. Dùng sandbox link chỉ khi file thực nằm trong sandbox; file Windows dùng link đường dẫn Windows. Hướng dẫn giải nén nội dung vào workspace root, không lồng thêm tên ZIP.

## Xác minh ở đích và checkpoint

| Tình huống | Trạng thái | Được khẳng định |
|---|---|---|
| Không truy cập được bytes ảnh | IMAGE_BINARY_UNAVAILABLE | Chưa có ZIP thật |
| ZIP đã đọc lại hợp lệ | ZIP_READY_FOR_DOWNLOAD | Có ảnh trong ZIP, chưa chứng minh có trên máy đích |
| Chờ giải nén | AWAITING_USER_EXTRACTION | Bước dùng ảnh còn thiếu file |
| Người dùng báo đã giải nén, chưa kiểm | AWAITING_REMOTE_VERIFICATION | Chưa đối chiếu hash đích |
| File đích giải mã được, đúng hash/path | OUTPUT_READY | Asset có thể dùng trong sản xuất |

Sau giải nén, đọc manifest và từng PNG trên đúng thiết bị. So hash/kích thước, decode thật bằng validator có sẵn. Lưu outputPaths/outputHashes, giữ ID và source hash. File thiếu/sai hash chặn đúng bước phụ thuộc; yêu cầu thẩm mỹ không chặn luồng mặc định.

Nếu người dùng chủ động yêu cầu nhìn ảnh, dùng [visual inspection](../openfilm-visual-inspection/SKILL.md). Chỉ ghi đã nhìn khi pixel thực được đưa vào ngữ cảnh; kiểm hash không chứng minh nội dung đẹp/đúng bố cục. Kết quả đánh giá tùy chọn không cấp quyền hoặc tự nghiệm thu macro.

Mẫu bàn giao: “ZIP có N PNG và manifest, đã kiểm SHA256. Giải nén vào [root thật]; ảnh đầu ở [path thật]. Sau khi đặt ảnh, tôi sẽ đối chiếu file đích để tiếp tục.” Không đặt yêu cầu VISUAL_PASS vào thông báo mặc định.

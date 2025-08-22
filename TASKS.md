# Danh sách công việc dự án IIIF All-Static Starter

Dưới đây là danh sách các công việc cần thực hiện để hoàn thành dự án.

- [ ] **1. Khởi tạo cấu trúc thư mục và các file cơ bản cho dự án:**
  - Tạo các thư mục: `config`, `data/masters`, `public/iiif/2`, `public/iiif/presentation`, `src`, `.github/workflows`.
  - Tạo các file trống ban đầu: `config/config.yaml`, `data/metadata.csv`, `src/tile_level0.py`, `src/build_manifest.py`, `src/utils.py`, `Makefile`, `requirements.txt`, `.gitignore`, `.github/workflows/build.yml`.

- [ ] **2. Viết script `tile_level0.py`:**
  - Đọc ảnh từ `data/masters`.
  - Tạo các ô ảnh (tiles) theo chuẩn IIIF Image API Level 0 (kích thước 512x512, định dạng webp/jpg).
  - Tạo file `info.json` tương ứng cho mỗi ảnh.
  - Lưu kết quả vào `public/iiif/2/`.

- [ ] **3. Viết script `build_manifest.py`:**
  - Đọc dữ liệu từ `data/metadata.csv`.
  - Tạo các file IIIF Presentation API v3 manifest (JSON-LD).
  - Lưu kết quả vào `public/iiif/presentation/`.

- [ ] **4. Tạo `Makefile`:**
  - `make tiles`: Chạy `src/tile_level0.py`.
  - `make manifests`: Chạy `src/build_manifest.py`.
  - `make all`: Thực hiện `tiles` và `manifests`.
  - `make serve`: Chạy server local để preview (`python -m http.server`).
  - `make clean`: Xóa các file đã tạo trong `public`.

- [ ] **5. Cấu hình GitHub Actions (CI/CD):**
  - Tạo workflow `.github/workflows/build.yml`.
  - Cài đặt dependencies từ `requirements.txt`.
  - Chạy `make all` để build.
  - Lưu các artifacts đã build.
  - (Tùy chọn) Thêm bước deploy lên Cloudflare R2 bằng `rclone`.

- [ ] **6. Viết script smoke test:**
  - Viết một script Python nhỏ để kiểm tra các đường dẫn trong manifest.
  - Đảm bảo các link tới `info.json`, canvas, thumbnail là hợp lệ.

- [ ] **7. Hoàn thiện tài liệu `README.md`:**
  - Hướng dẫn cài đặt môi trường.
  - Cách sử dụng `Makefile` để build và preview.
  - Hướng dẫn deploy lên các dịch vụ object storage (R2, S3, B2).
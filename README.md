# IIIF All-Static Starter

Repository này cung cấp một giải pháp hoàn chỉnh, chỉ sử dụng file tĩnh để phục vụ nội dung IIIF Image API Level 0 và Presentation API v2. Nó được thiết kế để loại bỏ sự cần thiết của một máy chủ hình ảnh IIIF chuyên dụng.

## Vấn đề & Giải pháp của chúng tôi

### Thách thức với hình ảnh độ phân giải cao

1.  **Số hóa tài liệu khổ lớn:** Khi số hóa bản đồ, bản thảo, hoặc các tác phẩm nghệ thuật khổ lớn, hình ảnh nguồn thường rất lớn (hàng trăm MB hoặc thậm chí GB).
    *   **Hiệu suất web:** Việc cung cấp trực tiếp các tệp lớn này đến trình duyệt web dẫn đến thời gian tải chậm và có thể dễ dàng làm treo trình duyệt của người dùng.
    *   **Chi phí băng thông:** Nó tiêu tốn một lượng băng thông khổng lồ.
    *   **Trải nghiệm người dùng:** Người xem thường chỉ cần phóng to và di chuyển để xem chi tiết, không cần tải toàn bộ tệp cùng một lúc.

2.  **Giải pháp động (Máy chủ hình ảnh truyền thống):**
    *   **Cách hoạt động:** Các máy chủ hình ảnh như Cantaloupe, Loris, hoặc IIPImage xử lý hình ảnh một cách linh hoạt theo yêu cầu (cắt, thay đổi kích thước, v.v.).
    *   **Nhược điểm:** Chúng yêu cầu một máy chủ phải chạy 24/7, tiêu tốn CPU và RAM. Cơ sở hạ tầng phức tạp để thiết lập và bảo trì, dẫn đến chi phí vận hành cao, đặc biệt đối với các tổ chức phi lợi nhuận.

3.  **Thách thức về Metadata:**
    *   Các thư viện và bảo tàng cần trình bày các tài liệu số với bối cảnh cấu trúc phong phú (ví dụ: một cuốn sách nhiều trang, một bản đồ có chú thích).
    *   Nếu không có một tiêu chuẩn như IIIF, mỗi tổ chức có thể phát minh ra định dạng độc quyền của riêng mình, dẫn đến thiếu khả năng tương tác giữa các bộ sưu tập và trình xem.

### Giải pháp "All-Static" (Dự án này)

Dự án này cung cấp một giải pháp thay thế đơn giản, hiệu quả về chi phí và mạnh mẽ.

1.  **Phân phối hình ảnh được tiêu chuẩn hóa (IIIF Image API Level 0):**
    *   Hình ảnh nguồn được **xử lý trước** thành các ô tĩnh và một tệp `info.json`.
    *   Các tài sản tĩnh này được phân phối qua Mạng phân phối nội dung (CDN).
    *   Người dùng có thể phóng to và di chuyển một cách mượt mà, vì trình xem chỉ tải các ô cụ thể cần thiết cho chế độ xem hiện tại.

2.  **Metadata được tiêu chuẩn hóa (IIIF Presentation API v2):**
    *   Metadata và thông tin cấu trúc được biên dịch thành một tệp JSON-LD tĩnh được gọi là **manifest**.
    *   Bất kỳ trình xem nào tương thích với IIIF (như Mirador hoặc Universal Viewer) đều có thể đọc ngay lập tức manifest này để hiển thị một trải nghiệm người dùng tương tác, phong phú.

3.  **Không cần máy chủ hình ảnh động:**
    *   Bằng cách tạo trước mọi thứ, chúng tôi loại bỏ sự cần thiết của một máy chủ chạy 24/7.
    *   Việc triển khai đơn giản như tải lên một thư mục các tệp tĩnh lên một nhà cung cấp lưu trữ đối tượng (như Cloudflare R2, Backblaze B2, hoặc AWS S3).
    *   Điều này dẫn đến **chi phí cực kỳ thấp**, làm cho nó trở thành một lựa chọn hoàn hảo cho các tổ chức di sản văn hóa, các nhà nghiên cứu và các tổ chức phi lợi nhuận.


## Tính năng

-   **IIIF Image API Level 0:** Tạo các ô hình ảnh được cắt sẵn và một tệp `info.json` cho mỗi hình ảnh nguồn.
-   **IIIF Presentation API v2:** Hỗ trợ tạo manifest cho IIIF Presentation API v2.
-   **Tĩnh & Không máy chủ:** Không có phụ thuộc thời gian chạy, giúp chi phí lưu trữ rẻ và dễ bảo trì.
-   **Quy trình làm việc tự động:** Sử dụng `Makefile` để hợp lý hóa quy trình xây dựng.
-   **Tùy chỉnh:** Cấu hình được quản lý thông qua một tệp `config.yaml` đơn giản.
-   **Tương thích đa nền tảng:** Hỗ trợ IIIF v2 cho các công cụ như AllMaps Editor.

## Cấu trúc dự án

```
.
├─ README.md
├─ INSTALL.md
├─ config/config.yaml
├─ data/masters/            # Đặt hình ảnh nguồn vào đây
├─ data/metadata.csv        # Metadata cho các manifest
│                           # Thông tin thư viện/bảo tàng cung cấp, thường dạng CSV /JSON / CSDL.
│                           # Chứa các trường: `object_id` (định danh tác phẩm / bản đồ / cuốn sách)
│                                               `image_id` (định danh file ảnh gốc)
│                                               `label`
│                                               `width` và `height`
│                                               Có thể kèm thêm: tác giả, năm xuất bản, nguồn, link mô tả chi tiết.
│ 
├─ public/                  # Thư mục đầu ra (triển khai thư mục này)
│   └─ iiif/
│       ├─ 2/               # Các ô Image API + info.json
│       └─ presentation/    # Các manifest Presentation API v2
├─ src/                     # Các script Python
│   ├─ tile_level0.py
│   ├─ build_manifest.py
│   └─ smoke_test.py
├─ Makefile
├─ requirements.txt
└─ venv/                    # Môi trường ảo Python
```

## Bắt đầu

Để biết hướng dẫn cài đặt chi tiết, vui lòng xem [INSTALL.md](./INSTALL.md).

## Cấu hình

### Cấu hình cơ bản

Dự án sử dụng file `config/config.yaml` cho cấu hình cơ bản:

```yaml
tile_size: 512
image_format: 'webp'
quality: 80
iiif_base_url: 'http://localhost:8080/iiif/2/'
```

### Biến môi trường (.env)

Bạn có thể ghi đè cấu hình bằng biến môi trường hoặc file `.env`:

1. **Sao chép file mẫu:**
   ```bash
   cp .env.example .env
   ```

2. **Chỉnh sửa `.env`:**
   ```bash
   # IIIF Base URL - Cập nhật với domain R2/S3/B2 của bạn
   IIIF_BASE_URL=https://your-r2-bucket.r2.dev/iiif/2/
   
   # Cài đặt xử lý ảnh
   TILE_SIZE=512
   IMAGE_FORMAT=webp
   QUALITY=80
   ```

3. **Kiểm tra cấu hình:**
   ```bash
   make show-config
   ```

### Biến môi trường triển khai

Để triển khai tự động, thêm thông tin xác thực vào `.env`:

```bash
# Cloudflare R2
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=your-bucket-name

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Backblaze B2
B2_KEY_ID=your-key-id
B2_APPLICATION_KEY=your-application-key
B2_BUCKET_NAME=your-bucket-name
```

## Quy trình làm việc

1. Dữ liệu đầu vào
    1.1 Ảnh gốc (Masters)

    * Các file số hoá (scan, chụp) dạng: TIFF, JPEG, PNG (thường là TIFF độ phân giải cao).
    * Kích thước rất lớn: ví dụ 12.000 × 8.000 px, dung lượng vài trăm MB.
    * Đây là nguồn gốc để sinh ra toàn bộ derivative.

    1.2 Metadata mô tả (Catalog)

    1.2.1 Thông tin thư viện/bảo tàng cung cấp, thường dạng CSV / JSON / Database format.

    1.2.2 Chứa các trường sau:

        - `object_id` (định danh cho tác phẩm nghệ thuật / bản đồ / sách)
        - `image_id` (định danh cho file ảnh gốc)
        - `label` (tiêu đề, mô tả ngắn)
        - `width`, `height` (có thể tự động đọc từ ảnh nếu không được cung cấp)

Có thể kèm thêm: tác giả, năm xuất bản, nguồn, link mô tả chi tiết.
Sơ đồ dưới đây minh họa quy trình làm việc từ đầu đến cuối, từ việc thêm dữ liệu của bạn đến việc triển khai các tài sản IIIF tĩnh.

```
                                     +-------------------------+
                                     |   Dữ liệu của bạn       |
                                     |-------------------------|
                                     | 🖼️ data/masters/*.jpg   |
                                     | 📄 data/metadata.csv    |
                                     +-----------+-------------+
                                                 |
                                                 | (Bạn thêm/chỉnh sửa các tệp này)
                                                 v
+---------------------------------+    +-------------------------+
|   IIIF All-Static Starter       |    |   Các lệnh Makefile     |
|---------------------------------|    |-------------------------|
| 🐍 src/tile_level0.py           |    | 🔨 make all             |
| 🐍 src/build_manifest.py        |    | 🖼️ make tiles           |
| 🐍 src/smoke_test.py            |    | 📄 make manifests       |
| ⚙️ config/config.yaml          |    | 🧪 make test            |
+---------------------------------+    | 🚀 make serve           |
               ^                       | 🧹 make clean           |
               |                       +-----------+-------------+
               | (Đọc cấu hình)                    |
               |                                   | (Bạn chạy các lệnh này)
               +-----------------------------------+
                                                 |
                                                 v
                                     +-------------------------+
                                     |   Đầu ra được tạo ra    |
                                     |-------------------------|
                                     | 🌍 public/              |
                                     |    ├── iiif/2/ (các ô)  |
                                     |    └── p/ (các manifest)|
                                     +-----------+-------------+
                                                 |

```

### Bắt đầu nhanh

1.  **Cài đặt các phụ thuộc:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Thêm hình ảnh nguồn:**
    Đặt các hình ảnh nguồn có độ phân giải cao của bạn vào thư mục `data/masters/`.

3.  **Xây dựng mọi thứ:**
    ```bash
    make all
    ```
    
    Lệnh này sẽ tự động:
    - Tạo `data/metadata.csv` từ các ảnh trong `data/masters/`
    - Tạo tiles và info.json cho từng ảnh
    - Tạo IIIF manifests cho từng object

## Các lệnh Makefile

Dự án này sử dụng `Makefile` để tự động hóa các tác vụ phổ biến.

### Lệnh cơ bản

-   `make all`
    Xây dựng mọi thứ với IIIF Presentation API v2: chạy `generate-metadata`, `tiles` và sau đó là `manifests`.

-   `make generate-metadata`
    Tự động tạo `data/metadata.csv` từ các hình ảnh trong `data/masters/`.

-   `make tiles`
    Tạo các ô hình ảnh và các tệp `info.json` từ các hình ảnh trong `data/masters/`.

### Lệnh tạo manifest

-   `make manifests`
    Tạo các manifest IIIF Presentation v2 từ `data/metadata.csv`.

### Lệnh khác

-   `make test`
    Chạy các kiểm tra sơ bộ để xác thực đầu ra được tạo ra (v2).

-   `make serve`
    Khởi động một máy chủ web cục bộ để xem trước thư mục `public` tại `http://localhost:8080`.

-   `make clean`
    Xóa tất cả các tệp được tạo ra trong thư mục `public`.

## IIIF API Version

### IIIF Presentation API v2

| Tính năng | IIIF Presentation API v2 |
|-----------|---------------------------|
| **JSON-LD Context** | `http://iiif.io/api/presentation/2/context.json` |
| **Manifest Type** | `sc:Manifest` |
| **Canvas Structure** | `sequences` → `canvases` → `images` |
| **Image Service** | `@id`, `@type: "ImageService2"` |
| **Tương thích** | Các công cụ như AllMaps Editor và nhiều trình xem IIIF |

## Cách hoạt động

1.  **Tạo metadata (`make generate-metadata`):**
    Script `src/generate_metadata.py` tự động quét thư mục `data/masters/`, phân tích tên file và kích thước ảnh để tạo ra `data/metadata.csv` với các object_id thông minh.

2.  **Tạo ô hình ảnh (`make tiles`):**
    Script `src/tile_level0.py` đọc mỗi hình ảnh từ `data/masters/`, tạo một tệp `info.json` tương ứng với các chi tiết cơ bản, và tạo ra một kim tự tháp các ô hình ảnh tĩnh theo các cài đặt trong `config/config.yaml`.

3.  **Tạo Manifest (`make manifests`):**
    Script `src/build_manifest.py` đọc `data/metadata.csv`, nhóm các hình ảnh vào các đối tượng tương ứng của chúng, và xây dựng manifest IIIF Presentation v2 cho mỗi đối tượng. Tuân thủ IIIF Presentation API 2.1 (tương thích với các công cụ như AllMaps Editor và nhiều trình xem IIIF).

## IIIF Image API URL Structure & Static Implementation

### URL Pattern Analysis

IIIF Image API URLs tuân theo cấu trúc chuẩn:
```
{scheme}://{server}{/prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}
```

**Ví dụ URL thực tế:**
```
https://static.ssan.me/iiif/2/Ninh_Binh_1924/0,0,2048,2048/512,/0/default.jpg
```

**Phân tích các thành phần:**
- **Base URL:** `https://static.ssan.me/iiif/2/`
- **Image Identifier:** `Ninh_Binh_1924`
- **Region:** `0,0,2048,2048` (x=0, y=0, width=2048, height=2048)
- **Size:** `512,` (width=512, height tỷ lệ)
- **Rotation:** `0` (không xoay)
- **Quality:** `default` (chất lượng gốc)
- **Format:** `jpg`

### Chiến lược tạo biến thể tĩnh

Dự án này sử dụng **phương pháp 4 chiều** để tạo ra các biến thể ảnh:

#### 1. **Region Variants (Vùng ảnh)**
- **Full regions:** `full`, `square` (vuông trung tâm)
- **Tile-based regions:** Lưới 512×512 pixel bao phủ toàn bộ ảnh
- **Test regions:** Các vùng nhỏ để kiểm tra (256×256, 200×200, v.v.)

#### 2. **Size Variants (Kích thước)**
- **Width-constrained (`w,`):** 100, 200, 400, 512, 600, 800, 1024, 1200, 1600, 2048
- **Height-constrained (`,h`):** Cùng giá trị như width
- **Exact sizing (`w,h`):** Kích thước chính xác (có thể méo tỷ lệ)
- **Best-fit (`!w,h`):** Vừa khung mà không méo tỷ lệ
- **Percentage (`pct:n`):** 10%, 25%, 50%, 75%, 90%
- **Special:** `full`, `max`

#### 3. **Rotation Variants (Xoay)**
- `0°` - Hướng gốc
- `90°` - Xoay thuận chiều kim đồng hồ
- `180°` - Xoay nửa vòng
- `270°` - Xoay ngược chiều kim đồng hồ

#### 4. **Quality Variants (Chất lượng)**
- `default` - Chế độ màu gốc
- `color` - RGB rõ ràng
- `gray` - Thang độ xám
- `bitonal` - Đen trắng (1-bit)

#### 5. **Format Variants (Định dạng)**
- **JPG** - Tương thích phổ biến, chất lượng có thể cấu hình
- **WebP** - Định dạng hiện đại, nén tốt hơn
- **PNG** - Không mất dữ liệu, hỗ trợ trong suốt

### Cấu trúc thư mục

Các biến thể được tổ chức theo mẫu URL IIIF:
```
public/iiif/2/{identifier}/{region}/{size}/{rotation}/{quality}.{format}
```

**Ví dụ:**
```
public/iiif/2/Ninh_Binh_1924/
├── 0,0,512,512/
│   ├── full/
│   │   ├── 0/
│   │   │   ├── default.jpg
│   │   │   ├── default.webp
│   │   │   ├── gray.jpg
│   │   │   └── bitonal.jpg
│   │   ├── 90/
│   │   └── 180/
│   ├── 512,/
│   └── pct:50/
├── full/
│   ├── full/
│   ├── 512,/
│   └── max/
└── square/
```

### Tối ưu hóa hiệu suất

- **Tạo có chọn lọc:** Không tạo tất cả tổ hợp có thể, chỉ tập trung vào các biến thể thường được yêu cầu
- **Cấu hình chất lượng:** JPEG quality 80%, WebP cho nén tốt hơn
- **Kích thước tile:** 512×512 tối ưu cho hiệu suất web
- **CDN-friendly:** URL bất biến với cache TTL dài

### Tuân thủ IIIF Level 0

Implementation này tuân thủ **IIIF Image API Level 0** bằng cách:
- Chỉ phục vụ các biến thể đã được tạo trước
- Cập nhật `info.json` để phản ánh chính xác khả năng
- Bao gồm ghi chú chi tiết về các biến thể có sẵn
- Không yêu cầu xử lý động

Ví dụ `info.json`:
```json
{
  "@context": "http://iiif.io/api/image/2/context.json",
  "@id": "https://static.ssan.me/iiif/2/Ninh_Binh_1924",
  "profile": [
    "http://iiif.io/api/image/2/level0.json",
    {
      "formats": ["jpg", "webp"],
      "qualities": ["default"],
      "note": "Static implementation with pre-generated variants only. Supports common sizes: 100,200,400,512,600,800,1024,1200,1600,2048 for width/height constraints, percentages: 10,25,50,75,90, and rotations: 0,90,180,270 degrees."
    }
  ]
}
```

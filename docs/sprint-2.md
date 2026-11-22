# Sprint 2 của đồ án

Sprint 2 kéo dài 2 tuần, nghiệm thu 2 lần:

| Nghiệm thu | Nội dung |
|---|---|
| **Đầu buổi 18/11** (nửa đầu, file này) | Test API, test route, data-driven, fixture và marker, 12 test giao diện |
| Đầu buổi 25/11 (nửa sau, giao ở buổi 3) | Feature BDD, GitHub Actions 3 trình duyệt, artifact |

Cần nộp cho 18/11:

1. Ít nhất **5 test API** (đề mục 3.5).
2. **2 test route** (đề mục 3.6).
3. **2 test `parametrize`**, 1 trong đó đọc dữ liệu từ file JSON hoặc CSV (đề mục 3.3).
4. `conftest.py` có **2 scope**, **đăng nhập một lần bằng `storage_state`**, **3 marker** (đề mục 3.4).
5. **12 test giao diện** phủ đủ 6 nhóm chức năng, ít nhất 8 test đã xanh (đề mục 3.2).
6. **PR #2** có một bạn khác review rồi mới merge.

Phần lớn mục 1 - 4 là các bài buổi 2 viết lại cho repo nhóm. Làm theo các bước dưới đây.

## Bước 1. Lấy bài giải buổi 2 về repo thực hành

Sau buổi 11/11, bài giải buổi 2 có trên nhánh `bai-giai` của repo lớp. Trong thư mục repo thực hành:

```bash
git fetch lop
git checkout lop/bai-giai -- tests/buoi2 data/search_keywords.json
pytest tests/buoi2                       # 23 passed
```

Muốn so trước khi lấy: `git diff HEAD lop/bai-giai -- tests/buoi2`.

## Bước 2. Chép sang repo nhóm, theo cấu trúc của đề

Đề mục 4 gợi ý chia `tests/` thành `ui/`, `api/`. Trong repo nhóm, tạo nhánh mới:

```bash
git checkout main
git pull
git checkout -b feature/<tên-em>-sprint2
```

| Tạo trong repo nhóm | Lấy từ repo thực hành |
|---|---|
| `tests/api/test_products_api.py` | B2.2 (cấu trúc JSON), B2.3 (tìm kiếm đọc từ JSON), B2.4a (4xx, parametrize) |
| `tests/api/test_users_api.py` | B2.4b (422), B2.5a (có token) |
| `tests/api/test_carts_api.py` | B2.6 (POST và GET, fixture `new_cart`) |
| `tests/ui/test_network.py` | B2.7 (chặn ảnh), B2.8 (danh sách rỗng) |
| `data/search_keywords.json` | File dữ liệu của B2.3 |

Đổi tên hàm cho đúng quy tắc đặt tên của đề: `test_<chức_năng>_<kịch_bản>_<kết_quả_mong_đợi>`, bỏ tiền tố `b2_x`. Ví dụ `test_b2_6_cart_add_product_quantity_two_is_stored` thành `test_cart_add_product_quantity_two_is_stored`.

Đường dẫn file JSON: dòng `Path(__file__).parents[2] / "data" / ...` tính từ vị trí file test. File ở `tests/api/` thì `parents[2]` là thư mục gốc repo, giữ nguyên được.

Đối chiếu đề mục 3.5:

| Đề yêu cầu | Test đáp ứng |
|---|---|
| ≥ 5 test API | B2.2, B2.3 (mỗi từ khoá 1 test), B2.4a (2 test), B2.4b, B2.5a, B2.6 |
| ≥ 2 phương thức HTTP | B2.6 (POST và GET) |
| ≥ 1 test lỗi 4xx | B2.4a, B2.4b |
| ≥ 1 test cấu trúc JSON | B2.2 |
| ≥ 1 test có token | B2.5a |

Đề mục 3.6: B2.7 là chặn tài nguyên, B2.8 là giả lập phản hồi và kiểm giao diện.

Đề mục 3.3: B2.3 (đọc từ JSON) và B2.4a là 2 test `parametrize`.

## Bước 3. Kiểm tra `conftest.py` và `pytest.ini` (đề mục 3.4)

`conftest.py` chép từ repo thực hành ở Sprint 1 đã có đủ:

| Đề yêu cầu | Có sẵn ở đâu |
|---|---|
| ≥ 2 scope | `api`, `test_user` là `session`; `logged_in_page` là `function` |
| Đăng nhập 1 lần, dùng lại `storage_state` | Fixture `auth_state` và `logged_in_page` |
| ≥ 3 marker, chạy được `pytest -m smoke` | `pytest.ini` khai báo `smoke`, `regression`, `ui`, `api`... |

Việc của nhóm: **dùng** chúng.

- Ít nhất 1 test giao diện cần đăng nhập dùng `logged_in_page` thay vì `page`.
- Gắn marker cho test: `@pytest.mark.api` cho test API, `@pytest.mark.ui` cho test giao diện, `@pytest.mark.smoke` cho vài test quan trọng nhất.

Kiểm tra marker chạy được:

```bash
pytest -m api --collect-only -q          # liệt kê test API
pytest -m smoke                          # vẫn xanh
```

## Bước 4. Đủ 12 test giao diện (đề mục 3.2)

Sprint 1 đã có 4 test smoke. Viết thêm ít nhất 8 test để đủ 12 và phủ đủ 6 nhóm chức năng:

| Nhóm chức năng | Đã có từ Sprint 1 | Gợi ý viết thêm |
|---|---|---|
| Danh sách và tìm kiếm | Tìm "pliers" | Tìm từ khoá không có (B1.2), sắp xếp theo giá (B1.7) |
| Bộ lọc | | Tích danh mục "Hammer": mọi sản phẩm hiện ra có chữ hammer |
| Chi tiết sản phẩm | Thêm 3 cái vào giỏ | Trang chi tiết hiện đúng tên và giá sản phẩm vừa bấm |
| Giỏ hàng | | Giá dòng bằng đơn giá nhân số lượng (B1.4), tiếp tục mua sắm (B1.6) |
| Xác thực | Đăng nhập sai | Form đăng nhập trống báo lỗi bắt buộc (B1.5) |
| Liên hệ, tài khoản | Form liên hệ trống | Trang tài khoản đã đăng nhập (dùng `logged_in_page`, giống B2.12) |

Đề mục 3.2 còn yêu cầu mỗi tình huống sau có ít nhất 1 test. **Cần có trước khi kết thúc Sprint 2 (25/11)**, làm sớm được thì tốt:

| Tình huống | Gợi ý trên Toolshop (đã chạy thử ngày 09/11) |
|---|---|
| Thanh trượt | Thanh trượt giá ở trang chủ: `page.get_by_role("slider").nth(1)` là nút bên phải. `focus()` rồi bấm phím `ArrowLeft`, mỗi lần giảm 1 đô. Trang tải lại danh sách bằng request `/products` có điều kiện `between=price,1,<giá tối đa>` |
| Tải tệp lên | Form Liên hệ có ô `attachment`, `ContactPage.attach(path)` có sẵn. Toolshop chỉ nhận tệp **rỗng** (0 byte); tệp có nội dung bị từ chối, đó cũng là một test hay |
| Tab mới | Link GitHub ở chân trang chủ (`data-test="footer-learn-github"`) mở tab mới. Bắt tab bằng `with page.context.expect_page() as info:` |

Locator mới cho các test này: thêm vào page object tương ứng trong `pages/`, không viết trong test.

## Bước 5. Chạy, kiểm luật, mở PR #2

```bash
pytest                                   # ít nhất 8 test giao diện và mọi test API, route xanh
grep -rn "import requests" tests         # không in gì
grep -rn "get_by_\|locator(" tests/      # không in gì
grep -rn "expect(\|assert " pages/       # không in gì
grep -rn "sleep\|wait_for_timeout" tests pages   # không in gì
```

Windows PowerShell: thay `grep -rn "<mẫu>" <thư mục>` bằng `Select-String -Path <thư mục>\*.py -Pattern "<mẫu>"`, ví dụ `Select-String -Path tests\*\*.py -Pattern "import requests"`.

```bash
git add tests data pages conftest.py
git status                               # KHÔNG được thấy .env
git commit -m "Add API, route and UI tests for Sprint 2"
git push -u origin feature/<tên-em>-sprint2
```

Mở Pull Request trên GitHub như Sprint 1 (`docs/sprint-1.md` bước 5). Mô tả PR chép kết quả `pytest` (dòng `... passed`). Một bạn khác review theo 5 câu:

1. Test có locator nào không? (phải không có)
2. `pages/` có `expect` hay `assert` không? (phải không có)
3. Có `sleep` hay `import requests` không? (phải không có)
4. Test API nào so số lượng tuyệt đối, ví dụ `total == 50`? (phải không có)
5. Test nào thiếu docstring 3 dòng?

## Nghiệm thu đầu buổi 18/11 (mỗi nhóm 1 phút)

Một bạn chiếu màn hình:

1. `pytest --collect-only -q`: đếm số test, thấy đủ test API, route, giao diện.
2. `pytest -m api`: xanh.
3. Tab **Pull requests** → **Closed**: PR #2 đã merge, có Approved của bạn khác.

Kẹt ở bước nào: chụp màn hình lỗi (cả lệnh đã gõ) gửi lên nhóm lớp.

# Buổi 2 (11/11) - API, chặn và giả lập mạng - Phiếu thực hành

Làm theo cặp: một bạn gõ (driver), một bạn đọc phiếu và soát luật (navigator). Xong mỗi bài thì đổi vai.

Mục tiêu cuối buổi: mọi test trong `tests/buoi2/` chuyển từ đỏ sang xanh. Bài có chữ **(thử thách)** làm khi còn thời gian, không kịp thì làm ở nhà.

Lý thuyết của từng bài nằm trong bài đọc `bai-doc/buoi-2-api-va-mang.md`, số mục ghi ở đầu mỗi bài.

## 0. Chuẩn bị (5 phút, trước khi bắt đầu)

1. Mở VS Code, **File > Open Folder**, mở thư mục `toolshop-practice` của em. Mở terminal (**Terminal > New Terminal**), bật môi trường ảo:

   ```powershell
   .venv\Scripts\activate          # Windows
   ```

   ```bash
   source .venv/bin/activate       # macOS / Linux
   ```

   Đầu dòng lệnh có chữ `(.venv)` là đúng.

2. **Lấy bài giải buổi 1** (bắt buộc, các bài B2.7 - B2.11 dùng `HomePage` của buổi 1):

   ```bash
   git remote add lop https://github.com/jameboykks/toolshop-practice.git   # bỏ qua nếu báo "already exists"
   git fetch lop
   git checkout lop/bai-giai -- pages tests/buoi1/test_b1_pom.py
   ```

3. **Kiểm tra máy và token GitHub:**

   ```bash
   python tools/doctor.py
   ```

   Dòng cuối phải là "Máy đã sẵn sàng". Dòng "GitHub API: còn .../5000 lượt" nghĩa là token đã chạy; ".../60 lượt" là chưa có token (xem Phần D để tạo, cả lớp chung 60 lượt mỗi giờ).

4. **Chạy thử trạng thái ban đầu:**

   ```bash
   pytest tests/buoi2 -m "not github"
   ```

   Đúng: `14 failed, 2 passed`. Hai bài xanh sẵn là B2.1 và B2.12.

5. Mở sẵn trên trình duyệt: Swagger của Toolshop https://api.practicesoftwaretesting.com/api/documentation và trang chủ https://practicesoftwaretesting.com (F12 mở DevTools).

### Ba file bài tập

| File | Bài |
|---|---|
| `tests/buoi2/test_b2_api.py` | B2.1 - B2.6: test API Toolshop |
| `tests/buoi2/test_b2_network.py` | B2.7 - B2.12: chặn, giả lập mạng, API giúp giao diện |
| `tests/buoi2/test_b2_github_api.py` | B2.13: GitHub API |
| `data/search_keywords.json` | Dữ liệu cho B2.3 |

Mỗi hàm chưa viết có dòng `raise NotImplementedError("B2.x")`. Xoá dòng đó, viết code thay vào, **Ctrl+S**, chạy lại. Số dòng ghi trong phiếu là của file gốc chưa gõ gì; gõ thêm ở phía trên thì các dòng dưới dịch xuống, khi đó dùng **Ctrl+F** tìm `B2.4` (đổi số theo bài).

### Luật buổi này (cũng là luật chấm đồ án)

1. Gọi API bằng fixture `api` (`APIRequestContext`), **không** `import requests`.
2. Không assert số lượng tuyệt đối (`total == 50`): PROD và BUGGY có dữ liệu khác nhau.
3. Không viết URL đầy đủ `https://...` trong test: đường dẫn bắt đầu bằng `/`, phần đầu lấy từ `API_URL`.
4. Mọi assert về `response.status` kèm `, response.text()` để khi đỏ thấy được server trả về gì.

### Đọc kết quả test API

```
>       assert response.status == 200, response.text()
E       AssertionError: {"message":"Unauthorized"}
E       assert 401 == 200
tests/buoi2/test_b2_api.py:92: AssertionError
```

| Dòng | Nghĩa |
|---|---|
| `E AssertionError: {"message":"Unauthorized"}` | Thân phản hồi server trả về: đọc dòng này trước |
| `E assert 401 == 200` | Server trả 401, test mong 200 |
| `tests/buoi2/test_b2_api.py:92` | File và dòng cần xem. Giữ Ctrl rồi bấm vào để mở đúng dòng |

### Fixture và hàm có sẵn trong `conftest.py`

| Tên | Loại | Trả về |
|---|---|---|
| `api` | fixture, session | `APIRequestContext`, gốc là `API_URL` |
| `test_user` | fixture, session | Tài khoản mới tạo qua API: `{"email", "password", "id"}` |
| `auth_token` | fixture, session | Token sau khi đăng nhập `test_user` |
| `auth_headers` | fixture, session | `{"Authorization": "Bearer <token>"}` |
| `logged_in_page` | fixture, function | Page đã đăng nhập sẵn (storage state) |
| `github` | fixture, session | `APIRequestContext` cho GitHub API |
| `new_email()` | hàm | Email ngẫu nhiên |
| `strong_password()` | hàm | Mật khẩu ngẫu nhiên đủ mạnh |
| `register_user(api, email, password)` | hàm | Đăng ký tài khoản, trả về phản hồi |

Muốn dùng fixture nào thì ghi tên nó vào danh sách tham số của hàm test. Ba hàm đã import sẵn ở dòng 13 của `test_b2_api.py`.

---

## Phần A - Test API Toolshop (`tests/buoi2/test_b2_api.py`)

### B2.1 - API còn sống không? (cùng giảng viên, 2 phút, bài đọc mục 2)

Đã viết sẵn ở dòng 19 - 25. Chạy và đọc:

```bash
pytest tests/buoi2 -k b2_1 -v
```

**Đạt khi:** `1 passed`. Đọc 3 dòng thân hàm: gọi `GET /status`, kiểm mã 200, kiểm `app_name`.

### B2.2 - Hợp đồng JSON của GET /products (8 phút, bài đọc mục 3)

**Mở:** `tests/buoi2/test_b2_api.py`, hàm `test_b2_2_...` (dòng 29), dòng `raise` ở dòng 35.

**Làm từng bước** (thay dòng `raise`, thụt 4 dấu cách):

1. Gọi `api.get("/products", params={"page": 1})`, kiểm mã 200.
2. Lấy `body = response.json()`. Kiểm có đủ 5 khoá: `current_page`, `data`, `per_page`, `total`, `last_page` (dùng vòng `for`).
3. Kiểm `0 < len(body["data"]) <= body["per_page"]`.
4. Với mỗi sản phẩm trong `body["data"]`: `id` là chuỗi hoặc số nguyên, `name` là chuỗi không rỗng, `price` là số lớn hơn 0.

**Chạy:** `pytest tests/buoi2 -k b2_2 -v`

**Đạt khi:** `1 passed`, và không có dòng nào so `total` với một con số.

<details><summary>Gợi ý</summary>

```python
assert isinstance(product["id"], (str, int))
assert isinstance(product["name"], str) and product["name"].strip()
```

PROD dùng id chuỗi (`01M6J...`), BUGGY dùng id số (`1`): `(str, int)` chấp nhận cả hai.

</details>

### B2.3 - Tìm kiếm data-driven từ JSON (7 phút, bài đọc mục 4)

**Mở:** `tests/buoi2/test_b2_api.py`, hàm `test_b2_3_...` (dòng 40), dòng `raise` ở dòng 45. Dòng 39 đã có `@pytest.mark.parametrize`, dòng 15 đã đọc file JSON vào `KEYWORDS`.

**Làm từng bước:**

1. Thay dòng `raise`: gọi `api.get("/products/search", params={"q": case["keyword"]})`, kiểm mã 200.
2. Lấy danh sách tên: `names = [p["name"] for p in response.json()["data"]]`.
3. Kiểm `names` không rỗng, và mọi tên (viết thường) chứa `case["must_contain"]`.
4. Chạy, thấy 2 test xanh (`[pliers]`, `[hammer]`).
5. Mở `data/search_keywords.json`, thêm 2 dòng `saw` và `wrench` theo đúng mẫu 2 dòng có sẵn. **Nhớ dấu phẩy** cuối dòng `hammer`.
6. Chạy lại, không sửa code: thấy 4 test.

**Chạy:** `pytest tests/buoi2 -k b2_3 -v`

**Đạt khi:** 4 test xanh: `[pliers]`, `[hammer]`, `[saw]`, `[wrench]`.

<details><summary>Gợi ý</summary>

```python
assert all(case["must_contain"] in n.lower() for n in names), names
```

File JSON sau khi thêm có 4 dòng giữa `[` và `]`, ba dòng đầu kết thúc bằng dấu phẩy.

</details>

### B2.4 - Lỗi 4xx (10 phút, bài đọc mục 5)

**B2.4a.** **Mở** dòng 49 - 51. Đây là bài duy nhất phải sửa cả dòng `def`:

1. Xoá dòng chú thích 49 (`# TODO B2.4a: ...`), thay bằng dòng decorator `@pytest.mark.parametrize("path, expected", [...])` với 2 cặp: `("/users/me", 401)` và `("/products/does-not-exist", 404)`.
2. Dòng `def` (dòng 50): thêm 2 tham số `path, expected` sau `api`.
3. Thay dòng `raise` (dòng 51) bằng: docstring (hàm này chưa có, đề bắt buộc mọi test có docstring), rồi gọi `api.get(path)`, kiểm mã bằng `expected`.

**B2.4b.** Hàm dòng 54, `raise` ở dòng 57. Gửi `POST /users/register` với thân rỗng `data={}`, kiểm mã 422, và JSON lỗi có khoá `email` và `password`.

**B2.4c (thử thách).** Hàm dòng 60, `raise` ở dòng 63. Đăng ký bằng `register_user(api, new_email(), "Welcome01!")`, kiểm 422 và JSON lỗi có khoá `password`.

**Chạy:** `pytest tests/buoi2 -k b2_4 -v`

**Đạt khi:** 4 test xanh: `b2_4a[/users/me-401]`, `b2_4a[/products/does-not-exist-404]`, `b2_4b`, `b2_4c`.

<details><summary>Gợi ý</summary>

```python
@pytest.mark.parametrize("path, expected", [("/users/me", 401), ("/products/does-not-exist", 404)])
def test_b2_4a_protected_or_missing_resource_returns_4xx(api, path, expected):
```

Gửi thân JSON bằng `data=`, không có `json=`.

</details>

### B2.5 - Token (5 phút, bài đọc mục 6.1)

**B2.5a.** Hàm dòng 67, `raise` ở dòng 70. Hàm đã có sẵn 3 tham số `api, auth_headers, test_user`. Gọi `GET /users/me` kèm `headers=auth_headers`, kiểm 200 và `email` trong phản hồi bằng `test_user["email"]`.

**B2.5b (thử thách).** Hàm dòng 73, `raise` ở dòng 76. Đăng ký tài khoản mới bằng `register_user(api, new_email(), strong_password())`, kiểm 201, và phản hồi **không** có khoá `password`.

**Chạy:** `pytest tests/buoi2 -k b2_5 -v`

**Đạt khi:** 2 test xanh.

### B2.6 - Tự viết fixture (8 phút, bài đọc mục 6.3)

**Mở:** dòng 80 - 85.

1. Ngay dưới dòng chú thích 80 (`# TODO B2.6: ...`), viết fixture `new_cart`: có dòng `@pytest.fixture`, nhận `api`, gọi `api.post("/carts")`, kiểm 201, trả về `response.json()["id"]`.
2. Dòng `def test_b2_6_...`: thêm `new_cart` vào tham số, sau `api`.
3. Thay dòng `raise`:
   - Lấy sản phẩm đầu tiên: `api.get("/products", params={"page": 1}).json()["data"][0]`.
   - Thêm vào giỏ: `api.post(f"/carts/{new_cart}", data={"product_id": ..., "quantity": 2})`, kiểm `.ok`.
   - Đọc giỏ: `api.get(f"/carts/{new_cart}").json()["cart_items"]`.
   - Kiểm đúng 1 dòng, `quantity` là 2, `product_id` đúng sản phẩm (so dạng chuỗi: `str(...) == str(...)`).

**Chạy:** `pytest tests/buoi2 -k b2_6 -v`

**Đạt khi:** `1 passed`. Test dùng 2 phương thức HTTP (POST và GET) và tự tạo dữ liệu của mình.

<details><summary>Gợi ý</summary>

```python
@pytest.fixture
def new_cart(api):
    response = api.post("/carts")
    assert response.status == 201, response.text()
    return response.json()["id"]
```

Fixture được ghi vào tham số của test, không gọi `new_cart(api)` trong thân test.

</details>

---

## Phần B - Chặn và giả lập mạng (`tests/buoi2/test_b2_network.py`)

### Quan sát trước (cả lớp, 3 phút, bài đọc mục 7.1)

Mở trang chủ Toolshop, F12, tab **Network**, ô lọc gõ `products`, tải lại trang (F5). Trả lời:

1. Danh sách sản phẩm được tải bằng phương thức HTTP nào? (Gợi ý: không phải GET.)
2. Gõ "pliers" vào ô tìm kiếm, bấm Search. Request mới đi tới đường dẫn nào?
3. Đọc dòng 18 của file: `PRODUCT_LIST = re.compile(r"/products(\?.*)?$")`. Giải thích cho bạn cặp vì sao nó không bắt nhầm request tìm kiếm.

### B2.7 - Chặn ảnh (8 phút, bài đọc mục 7.2 - 7.3)

**Mở:** hàm dòng 24, thay 3 dòng 27 - 29 (2 dòng chú thích và `raise`).

1. Tạo list rỗng `blocked = []`.
2. Viết hàm `block(route)`: thêm `route.request.url` vào `blocked`, rồi `route.abort()`.
3. `page.route(re.compile(r"\.(png|jpe?g|webp|avif|svg)(\?.*)?$"), block)`. **Trước** khi mở trang.
4. Mở trang: `home = HomePage(page).open()`.
5. Kiểm tên sản phẩm đầu tiên vẫn hiện, và `blocked` không rỗng.

**Chạy:** `pytest tests/buoi2 -k b2_7 --headed --slowmo 300`

**Đạt khi:** `1 passed`. Trên trình duyệt thấy sản phẩm hiện ra không có ảnh.

### B2.8 - Danh sách rỗng (7 phút, bài đọc mục 7.2)

**Mở:** hàm dòng 33, thay 2 dòng 36 - 37.

1. `page.route(PRODUCT_LIST, ...)` với handler `route.fulfill(status=200, content_type="application/json", body=json.dumps(EMPTY_PAGE))`. `EMPTY_PAGE` khai báo sẵn ở dòng 19.
2. Mở trang chủ.
3. Kiểm `home.no_results` có chữ `There are no products found.` và `home.product_names` có 0 phần tử (`to_have_count(0)`).

**Chạy:** `pytest tests/buoi2 -k b2_8 --headed --slowmo 300`

**Đạt khi:** `1 passed`.

### B2.9 - Server lỗi 500 (5 phút)

**Mở:** hàm dòng 41, thay dòng `raise` 44.

1. Route `PRODUCT_LIST` trả `route.fulfill(status=500, body="{}")`.
2. Mở trang chủ.
3. Kiểm ô tìm kiếm vẫn gõ được (`expect(home.search_box).to_be_editable()`) và 0 sản phẩm.

**Đạt khi:** `pytest tests/buoi2 -k b2_9` ra `1 passed`.

### B2.10 - Sửa phản hồi thật (thử thách, 5 phút)

**Mở:** hàm dòng 48, thay dòng `raise` 52. Đọc dòng gợi ý (Hint) trong docstring.

1. Viết hàm `patch(route)`: `response = route.fetch()`, `body = response.json()`, đổi `body["data"][0]["price"] = 999.99`, rồi `route.fulfill(response=response, json=body)`.
2. `page.route(PRODUCT_LIST, patch)`, mở trang chủ.
3. Kiểm giá đầu tiên (`home.product_prices.first`) có chữ `$999.99`.

**Đạt khi:** `pytest tests/buoi2 -k b2_10` ra `1 passed`.

---

## Phần C - API giúp test giao diện (`tests/buoi2/test_b2_network.py`)

### B2.11 - Bỏ qua form đăng nhập bằng token (thử thách, 5 phút, bài đọc mục 8.3)

**Mở:** hàm dòng 56, thay dòng `raise` 62. Hàm đã có tham số `auth_token`.

1. Chép dòng `page.add_init_script(...)` trong docstring (dòng 61) xuống làm dòng code đầu tiên, bỏ chữ `Hint:`.
2. Mở `AccountPage(page).open()`.
3. Kiểm tiêu đề `account.title` là `My account`, và `account.nav_menu` có chữ `QA Bot`.

**Đạt khi:** `pytest tests/buoi2 -k b2_11` ra `1 passed`.

### B2.12 - Đăng nhập một lần và chạy song song (giảng viên chạy mẫu, cả lớp trả lời, bài đọc mục 8.2 và 9)

1. Đọc test có sẵn ở dòng 66 - 71 và fixture `logged_in_page` trong `conftest.py` (dòng 153 - 157): test dùng page đã đăng nhập sẵn, không gõ form.
2. Giảng viên chạy trên máy chiếu (cả lớp không chạy cùng lúc, để không làm nghẽn Toolshop):

   ```bash
   pytest tests/buoi1 tests/buoi2 -m "not github" --durations=5
   pytest tests/buoi1 tests/buoi2 -m "not github" -n 4
   ```

3. Ghi lại 2 thời gian. Trả lời: với `-n 4`, fixture `test_user` (scope session) tạo bao nhiêu tài khoản? Vì sao email phải ngẫu nhiên?

---

## Phần D - GitHub API (`tests/buoi2/test_b2_github_api.py`, bài đọc mục 10)

**Giới hạn lượt gọi:** không có token, GitHub cho 60 lượt mỗi giờ cho mỗi địa chỉ IP. Cả lớp dùng chung mạng trường nên hết rất nhanh. Tạo token để có 5.000 lượt mỗi giờ cho riêng em:

1. github.com, ảnh đại diện, **Settings**, **Developer settings**, **Personal access tokens**, **Fine-grained tokens**, **Generate new token**.
2. Đặt tên (ví dụ `toolshop`), chọn hạn 30 ngày, không chọn quyền nào, bấm **Generate token**, chép token.
3. Mở `.env`, dán vào sau dấu `=` của dòng `GITHUB_TOKEN=`, Ctrl+S.
4. Chạy `python tools/doctor.py`: thấy ".../5000 lượt" là xong.

Không bao giờ commit `.env`, không dán token vào chat hay AI.

### B2.13 - Bốn test GitHub (10 phút)

| Bài | Hàm (dòng) | Dòng `raise` | Làm gì |
|---|---|---|---|
| **a** | dòng 22 | 27 | `github.get(f"/repos/{REPO}")`: 200, `full_name` bằng `REPO`, `language` là `Python`, `license["spdx_id"]` là `Apache-2.0`, `stargazers_count` là số nguyên lớn hơn 0, `archived` là `False` |
| **b** | dòng 31 | 35 | Người dùng không tồn tại: `github.get(f"/users/no-such-user-{uuid.uuid4().hex[:12]}")`: 404 và `message` là `Not Found` |
| **c** | dòng 39 | 44 | `github.get("/rate_limit")`: 200; đọc 2 header `x-ratelimit-limit`, `x-ratelimit-remaining`, đổi sang `int`, kiểm `0 <= remaining <= limit` |
| **d** (thử thách) | dòng 48 | 53 | `github.get(f"/repos/{REPO}/releases/latest")`: `tag_name` có dạng `v1.64.1`, và không cũ hơn bản Playwright đang cài (`importlib.metadata.version("playwright")`) |

**Chạy:** `pytest tests/buoi2/test_b2_github_api.py -v`

**Đạt khi:** 4 test xanh (3 nếu bỏ qua bài thử thách).

<details><summary>Gợi ý</summary>

- `response.headers` là dict, khoá viết thường: `response.headers["x-ratelimit-remaining"]`. Viết hoa thì `KeyError`.
- Bài d: so 2 phiên bản dạng tuple số: `tuple(int(x) for x in tag[1:].split("."))`.
- Bị chặn vì hết lượt: GitHub trả 403 hoặc 429, thông báo có chữ "rate limit exceeded". Đó không phải lỗi test của em. Thêm token.

</details>

---

## Kiểm tra cuối buổi

```bash
pytest tests/buoi2 -v                     # 23 passed
grep -rn "import requests" tests          # không in gì
grep -rn "https://" tests/buoi2           # 3 dòng, đều là chú thích hoặc docstring
```

Windows PowerShell: `Select-String -Path tests\*\*.py -Pattern "import requests"` và `Select-String -Path tests\buoi2\*.py -Pattern "https://"`.

---

## Bài về nhà = nửa đầu Sprint 2 đồ án (nghiệm thu đầu buổi 18/11)

Hướng dẫn từng bước: `docs/sprint-2.md` trong repo lớp.

1. Ít nhất 5 test API (đề mục 3.5): có 2 phương thức HTTP, 1 test lỗi 4xx, 1 test cấu trúc JSON, 1 test có token.
2. 2 test route (đề mục 3.6): 1 chặn tài nguyên, 1 giả lập phản hồi và kiểm giao diện.
3. 2 test `parametrize`, 1 trong đó đọc dữ liệu từ file JSON hoặc CSV (đề mục 3.3).
4. `conftest.py` có 2 scope, đăng nhập một lần bằng `storage_state`, 3 marker (đề mục 3.4).
5. 12 test giao diện phủ đủ 6 nhóm chức năng (đề mục 3.2), ít nhất 8 test đã xanh.
6. PR #2 có người khác review rồi mới merge.

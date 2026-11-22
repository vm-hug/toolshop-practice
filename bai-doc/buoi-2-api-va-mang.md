# Bài đọc buổi 2 - API, chặn và giả lập mạng, chạy song song

Buổi học ngày 11/11. Đọc lại sau buổi khoảng 35 phút. Mọi đoạn code trong bài đã chạy thật trên Toolshop và GitHub ngày 09/11/2026.

Sau bài này, em làm được:

1. Viết test API bằng `APIRequestContext`: kiểm mã trạng thái, cấu trúc JSON, lỗi 4xx, gọi API có token.
2. Đọc dữ liệu test từ file JSON bằng `parametrize`.
3. Tự viết fixture và chọn đúng phạm vi (scope) cho nó.
4. Dùng `page.route()` để chặn, giả lập và sửa phản hồi mạng.
5. Dùng API để chuẩn bị trạng thái cho test giao diện: đăng nhập một lần, tiêm token.
6. Chạy song song bằng pytest-xdist và hiểu nó ảnh hưởng gì tới fixture.
7. Kiểm thử một API công khai thật (GitHub) có giới hạn lượt gọi.

## 0. Chuẩn bị và cách chạy

### 0.1 Lấy bài giải buổi 1 trước

Các bài B2.7 đến B2.11 dùng `HomePage` của buổi 1 (`product_names`, `no_results`, `product_prices`, `search_box`). Chưa làm xong buổi 1 thì lấy bài giải về trước, nếu không các bài này đỏ vì `AttributeError: 'HomePage' object has no attribute 'no_results'`.

```bash
git fetch lop
git checkout lop/bai-giai -- pages tests/buoi1/test_b1_pom.py
pytest tests/buoi1                 # 13 passed
```

Chưa có remote `lop` thì chạy trước: `git remote add lop https://github.com/jameboykks/toolshop-practice.git` (README mục 6).

### 0.2 Ba file bài tập

| File | Bài | Trạng thái ban đầu |
|---|---|---|
| `tests/buoi2/test_b2_api.py` | B2.1 - B2.6: test API Toolshop | B2.1 đã viết sẵn, còn lại đỏ |
| `tests/buoi2/test_b2_network.py` | B2.7 - B2.12: chặn, giả lập mạng, API giúp giao diện | B2.12 đã viết sẵn, còn lại đỏ |
| `tests/buoi2/test_b2_github_api.py` | B2.13: GitHub API | 4 test đỏ |

Mỗi hàm chưa viết có dòng `raise NotImplementedError("B2.x")`. Làm bài nào thì xoá dòng đó và viết code thay vào. Chạy lần đầu, trước khi làm gì: `pytest tests/buoi2 -m "not github"` ra `14 failed, 2 passed`.

### 0.3 Lệnh chạy

```bash
pytest tests/buoi2 -k b2_2 -v                    # một bài
pytest tests/buoi2/test_b2_api.py -v             # cả file API
pytest tests/buoi2 -k b2_8 --headed --slowmo 300 # xem trình duyệt chạy (bài mạng)
pytest tests/buoi2 -m "not github"               # bỏ qua bài GitHub khi mạng hết lượt
```

`-k b2_4` chạy mọi test có `b2_4` trong tên: cả `b2_4a`, `b2_4b`, `b2_4c`.

### 0.4 Đọc lỗi của test API

Test API đỏ thường có dạng:

```
>       assert response.status == 200, response.text()
E       AssertionError: {"message":"Unauthorized"}
E       assert 401 == 200
tests/buoi2/test_b2_api.py:92: AssertionError
```

- Dòng `E AssertionError: {...}` là **thân phản hồi của server**, có được nhờ `, response.text()` ở cuối dòng assert. Đọc dòng này trước: server nói vì sao từ chối.
- Dòng `assert 401 == 200`: server trả 401, test mong 200.
- Dòng cuối là file và số dòng cần xem.

Vì vậy mọi assert về `response.status` trong bài đều kèm `, response.text()`.

## 1. Khi nào kiểm thử qua API

```
        /\        Giao diện: điều người dùng thấy và bấm. Ít, chọn lọc.
       /  \
      /----\      API: logic, mã lỗi, phân quyền, dữ liệu. Nhiều hơn, ổn định hơn.
     /      \
    /--------\    Đơn vị: phần của lập trình viên.
```

Test API kiểm được logic mà không phụ thuộc giao diện, nên ít vỡ vặt khi giao diện đổi. API còn là cách nhanh để chuẩn bị dữ liệu cho test giao diện: tạo tài khoản, tạo giỏ hàng, đăng nhập.

**Đo, đừng đoán.** Cùng kiểm tra "giỏ có 2 sản phẩm", một test đi qua giao diện (B1.4), một test gọi API (B2.6):

| Ngày đo | Test giao diện B1.4 | Test API B2.6 |
|---|---|---|
| 02/11/2026 | 5,9 giây | 7,0 giây |
| 09/11/2026 | 6,7 giây | 3,7 giây |

Cùng hai test, hai ngày ra hai kết luận ngược nhau, vì Toolshop là site công cộng, tốc độ API phụ thuộc lúc đó có bao nhiêu người dùng. Trên hệ thống nội bộ, test API thường nhanh hơn test giao diện nhiều lần. Muốn biết test nào chậm trên máy em hôm nay, chạy `pytest --durations=5`.

Giá trị lâu dài của test API là **ổn định và cô lập được logic**, không phải tốc độ.

## 2. APIRequestContext

Playwright có sẵn một HTTP client. Đề đồ án yêu cầu dùng nó, không dùng thư viện `requests`, để giao diện và API đi chung một framework.

Fixture `api` trong `conftest.py` (dòng 61 - 68):

```python
@pytest.fixture(scope="session")
def api(playwright, api_url):
    context = playwright.request.new_context(
        base_url=api_url,                                  # lấy từ API_URL, không viết cứng
        extra_http_headers={"Accept": "application/json"},
    )
    yield context
    context.dispose()
```

Gọi API:

| Gọi | Ví dụ |
|---|---|
| GET có tham số | `api.get("/products", params={"page": 1})` |
| POST có thân JSON | `api.post(f"/carts/{cart_id}", data={"product_id": pid, "quantity": 2})` |
| Có header | `api.get("/users/me", headers=auth_headers)` |

Thân JSON truyền bằng `data=`, không có tham số `json=`. Viết `json={}` sẽ báo `TypeError: APIRequestContext.post() got an unexpected keyword argument 'json'`.

Những gì hay dùng trên một phản hồi:

| Thuộc tính, hàm | Trả về |
|---|---|
| `response.status` | Mã trạng thái, ví dụ `201` |
| `response.ok` | `True` với mọi mã 2xx |
| `response.json()` | Thân phản hồi dạng dict hoặc list |
| `response.text()` | Thân phản hồi dạng chuỗi, in ra khi assert đỏ |
| `response.headers` | Dict các header, khoá viết thường |

Test API đầu tiên (B2.1, có sẵn trong `tests/buoi2/test_b2_api.py` dòng 19 - 25):

```python
@pytest.mark.smoke
@pytest.mark.api
def test_b2_1_status_returns_toolshop(api):
    """Goal: API is alive. Precondition: none. Expected: 200 and app_name Toolshop."""
    response = api.get("/status")
    assert response.status == 200, response.text()
    assert response.json()["app_name"] == "Toolshop"
```

Mọi endpoint của Toolshop có trong Swagger: https://api.practicesoftwaretesting.com/api/documentation . Bấm vào một endpoint, bấm **Try it out**, **Execute** là thấy phản hồi thật.

## 3. Kiểm hợp đồng JSON

### 3.1 Kiểm mã cụ thể

`assert response.ok` chấp nhận cả 200, 201, 204. Khi biết rõ tạo mới phải trả 201, hãy kiểm `== 201`. Assertion càng cụ thể càng bắt được nhiều lỗi.

### 3.2 Kiểm cấu trúc, không kiểm con số

PROD và BUGGY là hai môi trường có dữ liệu khác nhau:

| | PROD | BUGGY |
|---|---|---|
| Số sản phẩm | 50 | 26 |
| Kiểu id | chuỗi, ví dụ `01M6J14DVMYNJHH0W6WN76M48N` | số nguyên, ví dụ `1` |

Site lại dùng chung với nhiều người, nên dữ liệu còn thay đổi theo ngày. Kiểm hành vi và cấu trúc, không kiểm con số:

```python
response = api.get("/products", params={"page": 1})
assert response.status == 200, response.text()
body = response.json()
for key in ("current_page", "data", "per_page", "total", "last_page"):
    assert key in body, f"missing key {key}"
assert 0 < len(body["data"]) <= body["per_page"]
for product in body["data"]:
    assert isinstance(product["id"], (str, int))
    assert isinstance(product["name"], str) and product["name"].strip()
    assert isinstance(product["price"], (int, float)) and product["price"] > 0
```

Không có dòng nào viết `total == 50`. `isinstance(product["id"], (str, int))` chấp nhận cả id chuỗi của PROD và id số của BUGGY.

## 4. Data-driven: đọc dữ liệu từ file

`tests/buoi2/test_b2_api.py` dòng 15 đọc file `data/search_keywords.json`:

```python
KEYWORDS = json.loads((Path(__file__).parents[2] / "data" / "search_keywords.json").read_text())
```

File có 2 dòng, mỗi dòng một từ khoá:

```json
[
  {"keyword": "pliers", "must_contain": "pliers"},
  {"keyword": "hammer", "must_contain": "hammer"}
]
```

`parametrize` biến mỗi dòng thành một test:

```python
@pytest.mark.parametrize("case", KEYWORDS, ids=[c["keyword"] for c in KEYWORDS])
def test_b2_3_search_api_returns_only_matching_names(api, case):
    response = api.get("/products/search", params={"q": case["keyword"]})
    assert response.status == 200, response.text()
    names = [p["name"] for p in response.json()["data"]]
    assert names, f"no results for {case['keyword']}"
    assert all(case["must_contain"] in n.lower() for n in names), names
```

Thêm một dòng vào file JSON là có thêm một test, không sửa code. `ids=` đặt tên dễ đọc cho từng test: báo cáo hiện `test_b2_3_...[pliers]` thay vì `test_b2_3_...[case0]`.

Thêm dòng vào JSON nhớ dấu phẩy giữa các dòng. Thiếu dấu phẩy thì cả file test không chạy được: `json.decoder.JSONDecodeError: Expecting ',' delimiter`.

## 5. Lỗi 4xx

### 5.1 Một hàm, nhiều trường hợp

```python
@pytest.mark.parametrize("path, expected", [("/users/me", 401), ("/products/does-not-exist", 404)])
def test_b2_4a_protected_or_missing_resource_returns_4xx(api, path, expected):
    response = api.get(path)
    assert response.status == expected, response.text()
```

Một hàm, hai test: `[/users/me-401]` và `[/products/does-not-exist-404]`. Tên trong `parametrize` (`"path, expected"`) phải có mặt trong danh sách tham số của hàm. Quên thêm vào hàm thì pytest báo `function uses no argument 'path'` và cả file không chạy.

### 5.2 Lỗi theo từng trường

Gửi form đăng ký rỗng, Toolshop trả 422 kèm danh sách lỗi theo từng trường:

```python
response = api.post("/users/register", data={})
assert response.status == 422, response.text()
errors = response.json()
assert "email" in errors and "password" in errors, errors
```

### 5.3 Mật khẩu từng bị lộ bị từ chối

Toolshop chặn mật khẩu từng xuất hiện trong các vụ lộ dữ liệu. Đăng ký bằng `Welcome01!` nhận 422, lỗi ở trường `password`: "The given password has appeared in a data leak". Vì vậy `conftest.py` có hàm `strong_password()` sinh mật khẩu ngẫu nhiên.

Hàm hỗ trợ trong `conftest.py`, đã import sẵn ở dòng 13 của `test_b2_api.py`:

| Hàm | Làm gì |
|---|---|
| `new_email()` | Email ngẫu nhiên, ví dụ `qa-3f9a1c2b7d4e@example.com` |
| `strong_password()` | Mật khẩu ngẫu nhiên đủ mạnh |
| `register_user(api, email, password)` | Đăng ký, tự thử cả 2 kiểu dữ liệu của PROD và BUGGY, trả về phản hồi |

## 6. Token và fixture

### 6.1 Chuỗi fixture có sẵn

| Fixture | Phạm vi | Làm gì |
|---|---|---|
| `test_user` | session | Tạo tài khoản mới qua `POST /users/register`, trả `{"email", "password", "id"}` |
| `auth_token` | session | `POST /users/login` bằng tài khoản đó, lấy `access_token` |
| `auth_headers` | session | `{"Authorization": "Bearer <token>"}` |

Test chỉ cần ghi tên fixture vào danh sách tham số, pytest tự tạo và truyền vào:

```python
def test_b2_5a_users_me_with_token_returns_own_profile(api, auth_headers, test_user):
    response = api.get("/users/me", headers=auth_headers)
    assert response.status == 200, response.text()
    assert response.json()["email"] == test_user["email"]
```

Quên `headers=auth_headers` thì server trả `{"message":"Unauthorized"}` và 401.

**Mỗi nhóm dùng tài khoản riêng cho test có ghi dữ liệu.** Tài khoản mẫu `customer@...` cả lớp dùng chung, chỉ để đọc.

### 6.2 Phạm vi (scope) của fixture

| Scope | Tạo lại khi nào | Dùng cho |
|---|---|---|
| `function` (mặc định) | Mỗi test | Thứ cần cách ly: page, context, giỏ hàng |
| `module` | Mỗi file test | Ít dùng trong đồ án |
| `session` | Một lần cho cả phiên chạy | Thứ đắt và chỉ đọc: API context, tài khoản, token |

### 6.3 Tự viết fixture

Ví dụ một giỏ hàng mới cho mỗi test (B2.6):

```python
@pytest.fixture
def new_cart(api):
    response = api.post("/carts")
    assert response.status == 201, response.text()
    return response.json()["id"]


def test_b2_6_cart_add_product_quantity_two_is_stored(api, new_cart):
    product = api.get("/products", params={"page": 1}).json()["data"][0]
    added = api.post(f"/carts/{new_cart}", data={"product_id": product["id"], "quantity": 2})
    assert added.ok, added.text()
    items = api.get(f"/carts/{new_cart}").json()["cart_items"]
    assert len(items) == 1
    assert items[0]["quantity"] == 2
    assert str(items[0]["product_id"]) == str(product["id"])
```

Ba điều hay nhầm:

- Fixture được **ghi vào tham số** của test, không gọi như hàm. Viết `new_cart(api)` trong thân test thì pytest báo `Fixture "new_cart" called directly`.
- Quên ghi `new_cart` vào tham số thì trong thân test, `new_cart` là chính hàm fixture chứ không phải id giỏ. URL thành `/carts/<pytest_fixture(...)>` và server trả `{"message":"Cart not found"}`.
- Fixture viết trong file test thì chỉ file đó dùng được. Muốn dùng ở nhiều file thì chuyển vào `conftest.py`.

## 7. Chặn và giả lập mạng với `page.route()`

### 7.1 Xem request thật trước khi viết pattern

Mở trang chủ Toolshop, F12, tab **Network**, lọc `products`:

| Môi trường | Request tải danh sách sản phẩm | Request khi tìm kiếm |
|---|---|---|
| PROD | `QUERY https://api.practicesoftwaretesting.com/products` | `QUERY .../products/search` |
| BUGGY | `GET https://api-with-bugs.practicesoftwaretesting.com/products?between=price,1&page=1` | |

QUERY là một phương thức HTTP mới, gửi điều kiện tìm trong thân request thay vì trên URL. Glob `**/products?*` không bắt được request của PROD vì URL không có dấu `?`. File `tests/buoi2/test_b2_network.py` dòng 18 dùng regex bắt được cả hai môi trường:

```python
PRODUCT_LIST = re.compile(r"/products(\?.*)?$")
```

- `/products`, rồi
- `(\?.*)?`: có thể có hoặc không có phần `?...` phía sau,
- `$`: hết URL. Nhờ dấu `$`, regex không bắt nhầm `/products/search` hay `/products/{id}`.

### 7.2 Ba cách can thiệp một request

```python
# Chặn: trang vẫn dùng được khi không có ảnh
page.route(re.compile(r"\.(png|jpe?g|webp|avif|svg)(\?.*)?$"), lambda route: route.abort())

# Giả lập: trả về phản hồi tự viết
page.route(PRODUCT_LIST, lambda route: route.fulfill(
    status=200, content_type="application/json", body=json.dumps(EMPTY_PAGE)))

# Sửa phản hồi thật
def patch(route):
    response = route.fetch()          # gọi server thật
    body = response.json()
    body["data"][0]["price"] = 999.99
    route.fulfill(response=response, json=body)
page.route(PRODUCT_LIST, patch)
```

Hai điều bắt buộc:

- **Đăng ký route trước khi mở trang.** Đăng ký sau `open()` thì request đã đi mất, route không chặn được gì.
- **`body=` phải là chuỗi.** Truyền dict vào `body=` thì Playwright báo `Route.fulfill: body: expected string, got object`. Dùng `body=json.dumps(...)`, hoặc tham số `json=` như cách thứ ba.

### 7.3 Test phải chứng minh điều kiện của chính nó

Test chặn ảnh chỉ kiểm "sản phẩm vẫn hiện" thì vẫn xanh khi route viết sai và không chặn gì. Ghi lại URL bị chặn, rồi kiểm danh sách đó không rỗng:

```python
blocked = []

def block(route):
    blocked.append(route.request.url)
    route.abort()

page.route(re.compile(r"\.(png|jpe?g|webp|avif|svg)(\?.*)?$"), block)
home = HomePage(page).open()
expect(home.product_names.first).to_be_visible()
assert blocked, "no image request was blocked"
```

Nguyên tắc: mock để tạo tình huống khó tạo bằng dữ liệu thật (danh sách rỗng, lỗi 500), không mock để test xanh.

## 8. API giúp test giao diện

### 8.1 Browser, context, page

| | Là gì | Ví dụ |
|---|---|---|
| Browser | Một tiến trình trình duyệt | Chromium |
| Context | Một phiên độc lập: cookie, localStorage riêng, giống cửa sổ ẩn danh | Mỗi test một context |
| Page | Một tab trong context | Trang Toolshop đang mở |

Tạo context chỉ mất vài mili giây, nên mỗi test một context: test này không để lại giỏ hàng hay phiên đăng nhập cho test khác.

### 8.2 Đăng nhập một lần, dùng lại nhiều lần (B2.12, có sẵn)

Fixture `auth_state` (`conftest.py` dòng 137 - 150) đăng nhập qua giao diện **một lần mỗi phiên** rồi lưu cookie và localStorage vào file. Fixture `logged_in_page` (dòng 153 - 157) mở context mới từ file đó cho từng test:

```python
@pytest.fixture
def logged_in_page(new_context, auth_state):
    context = new_context(storage_state=auth_state)
    return context.new_page()
```

Được: tiết kiệm một lần đăng nhập cho mỗi test. Rủi ro: token có thể hết hạn giữa chừng, và file trạng thái chứa token không được commit. Đề đồ án mục 3.4 yêu cầu đúng điều này: "đăng nhập 1 lần, tái sử dụng storage_state".

### 8.3 Bỏ qua form đăng nhập bằng token (B2.11)

Toolshop giữ token trong localStorage, khoá `auth-token`. `add_init_script` chạy **trước** mã của trang, nên token có sẵn khi Toolshop khởi động:

```python
page.add_init_script(f"window.localStorage.setItem('auth-token', {json.dumps(auth_token)})")
account = AccountPage(page).open()
expect(account.title).to_have_text("My account")
expect(account.nav_menu).to_contain_text("QA Bot")
```

"QA Bot" là tên của tài khoản `test_user` (`register_user` đăng ký với tên QA, họ Bot). Đặt token bằng `page.evaluate(...)` sau khi trang đã mở thì quá muộn: Toolshop đã khởi động không có token, menu người dùng không hiện.

## 9. Chạy song song

```bash
pytest tests/buoi1 tests/buoi2 -m "not github"            # tuần tự
pytest tests/buoi1 tests/buoi2 -m "not github" -n 4       # 4 tiến trình song song
```

Đo ngày 09/11/2026 trên máy 8 nhân: tuần tự 98 giây, `-n 4` còn 32 giây, cùng 32 test.

Mỗi tiến trình (worker) của pytest-xdist là một phiên pytest riêng. Vì vậy fixture `scope="session"` chạy **một lần cho mỗi worker**: `-n 4` tạo 4 tài khoản `test_user`. Email phải duy nhất, nếu không thì lần đăng ký thứ hai nhận 409 "A customer with this email address already exists." Hàm `new_email()` sinh email ngẫu nhiên vì lý do này.

Trên CI, đồ án dùng `-n 2`: máy của GitHub có 2 nhân, và Toolshop là site dùng chung, bắn quá nhiều luồng vào sẽ tự tạo ra test chập chờn.

**Tắt JavaScript không giúp gì với Toolshop.** Mở context với `java_script_enabled=False` thì trang Toolshop trắng hoàn toàn, vì nó là ứng dụng Angular dựng giao diện bằng JavaScript.

## 10. GitHub API

Nội dung học phần có mục "Thực hành tương tác với GitHub API". Cùng `APIRequestContext`, nhưng là một API công khai thật, khác Toolshop ở ba điểm:

- **Header phiên bản.** GitHub yêu cầu `Accept: application/vnd.github+json` và khuyên gửi `X-GitHub-Api-Version`, để API đổi phiên bản không làm vỡ client cũ.
- **Thân lỗi chuẩn.** Tài nguyên không tồn tại trả 404 với `{"message": "Not Found", ...}`.
- **Giới hạn lượt gọi.** Không có token: 60 lượt mỗi giờ cho mỗi địa chỉ IP, cả lớp dùng chung mạng trường là chung 60 lượt. Có token cá nhân: 5.000 lượt mỗi giờ cho riêng em. Mọi phản hồi đều kèm header `x-ratelimit-limit`, `x-ratelimit-remaining`. Riêng `GET /rate_limit` không bị tính lượt.

Fixture `github` trong `conftest.py` (dòng 71 - 84) tự gửi 2 header trên, và thêm token nếu `.env` có `GITHUB_TOKEN`.

Ví dụ kiểm thông tin một repo:

```python
response = github.get(f"/repos/{REPO}")
assert response.status == 200, response.text()
repo = response.json()
assert repo["full_name"] == REPO
assert repo["license"]["spdx_id"] == "Apache-2.0"
assert isinstance(repo["stargazers_count"], int) and repo["stargazers_count"] > 0
```

Số sao thay đổi mỗi ngày, nên test kiểm kiểu và dấu, không kiểm con số. Cùng nguyên tắc với dữ liệu Toolshop ở mục 3.2.

Đọc header: `response.headers` là dict có **khoá viết thường**. `response.headers["x-ratelimit-limit"]` chạy được, `response.headers["X-RateLimit-Limit"]` báo `KeyError`. Giá trị header là chuỗi, đổi sang số bằng `int(...)`.

**Tạo token:** github.com, ảnh đại diện, **Settings**, **Developer settings**, **Personal access tokens**, **Fine-grained tokens**, **Generate new token**. Đặt tên, chọn hạn, không cần chọn quyền nào (chỉ đọc dữ liệu công khai). Chép token vào dòng `GITHUB_TOKEN=` trong `.env`. Kiểm tra bằng `python tools/doctor.py`: dòng "GitHub API: còn .../5000 lượt gọi trong giờ này" là token đã chạy.

Token là mật khẩu: không commit, không dán vào chat hay AI. Lỡ lộ thì xoá token trên GitHub ngay.

Khi hết lượt, GitHub trả 403 hoặc 429 với thông báo có chữ "rate limit exceeded". Test đỏ vì lý do này không phải lỗi của test: đó là giới hạn của hệ thống bên ngoài. Trên GitHub Actions, workflow có sẵn token tự động (`secrets.GITHUB_TOKEN`), buổi 3 sẽ dùng.

## 11. Lỗi thường gặp

| Pytest in ra | Nguyên nhân | Sửa |
|---|---|---|
| `AttributeError: 'HomePage' object has no attribute 'no_results'` | Chưa có bài giải buổi 1 | Mục 0.1 |
| `TypeError: ... unexpected keyword argument 'json'` | `api.post(..., json=...)` | Dùng `data=` |
| `function uses no argument 'path'` | Có `parametrize` nhưng hàm thiếu tham số | Thêm `path, expected` vào hàm |
| `fixture 'path' not found` | Thêm tham số vào hàm nhưng quên dòng `@pytest.mark.parametrize` | Thêm dòng decorator |
| `JSONDecodeError: Expecting ',' delimiter` | File JSON thiếu dấu phẩy | Sửa file `data/search_keywords.json` |
| `{"message":"Unauthorized"}` và `assert 401 == 200` | Gọi `/users/me` không kèm token | `headers=auth_headers` |
| `Fixture "new_cart" called directly` | Gọi fixture như hàm | Ghi `new_cart` vào tham số của test |
| `{"message":"Cart not found"}` | Quên ghi `new_cart` vào tham số | Thêm vào tham số |
| `AssertionError: no image request was blocked` | Đăng ký route sau khi mở trang | Đặt `page.route(...)` trước `open()` |
| `Route.fulfill: body: expected string, got object` | `body=EMPTY_PAGE` (dict) | `body=json.dumps(EMPTY_PAGE)` |
| `Locator expected to have text 'There are no products found.'` sau 15 giây | Pattern không khớp request QUERY, ví dụ `"**/products?*"` | Dùng `PRODUCT_LIST` |
| Menu người dùng không hiện ở B2.11 | Đặt token bằng `evaluate` sau khi mở trang | `add_init_script` trước `open()` |
| `KeyError: 'X-RateLimit-Limit'` | Khoá header viết hoa | Viết thường: `x-ratelimit-limit` |
| GitHub 403 hoặc 429 "rate limit exceeded" | Hết lượt gọi của IP | Thêm `GITHUB_TOKEN` vào `.env` |
| Đăng ký nhận 409 "already exists" | Email cố định, hoặc chạy song song với email không ngẫu nhiên | `new_email()` |

## 12. Đếm lại và tự kiểm tra

Cuối buổi:

```bash
pytest tests/buoi2 -v                     # 23 passed (sau khi thêm saw, wrench vào JSON)
grep -rn "import requests" tests          # không in gì
grep -rn "https://" tests/buoi2           # 3 dòng, đều là chú thích hoặc docstring, không có URL trong code
```

Câu hỏi tự kiểm tra:

1. `assert response.ok` và `assert response.status == 201` khác nhau thế nào? Khi nào dùng cái nào?
2. Vì sao test API của nhóm không nên kiểm `total == 50`?
3. Chạy `pytest -n 4`, fixture `test_user` chạy mấy lần? Vì sao email phải ngẫu nhiên?
4. Vì sao route phải đăng ký trước khi mở trang?
5. Glob `**/products?*` có bắt được request tải danh sách sản phẩm trên PROD không? Vì sao?
6. `storage_state` tiết kiệm được gì, và có rủi ro gì?
7. Kể hai tình huống nên kiểm thử qua API thay vì qua giao diện.
8. Vì sao test GitHub không kiểm `stargazers_count == 15084`? Test đỏ vì "rate limit exceeded" là lỗi của ai?

## 13. Liên hệ đồ án

- Đề mục 3.3 Data-driven, 3.4 Fixture và marker, 3.5 Test API, 3.6 Route và mocking, 3.11 chạy song song. Nội dung học phần 6.1 đến 6.4.
- Câu vấn đáp 3, 4, 8, 10, 14.
- Bài về nhà (nửa đầu Sprint 2, nghiệm thu 18/11): `docs/sprint-2.md` trong repo lớp.

## 14. Đọc thêm

- API testing: https://playwright.dev/python/docs/api-testing
- Network, route: https://playwright.dev/python/docs/network
- Fixture của pytest: https://docs.pytest.org/en/stable/how-to/fixtures.html
- Parametrize: https://docs.pytest.org/en/stable/how-to/parametrize.html
- pytest-xdist: https://pytest-xdist.readthedocs.io/
- GitHub REST API: https://docs.github.com/en/rest
- Giới hạn lượt gọi của GitHub: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api

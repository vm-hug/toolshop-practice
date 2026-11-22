# Buổi 3 (18/11) - BDD và GitHub Actions - Phiếu thực hành

Làm theo cặp trong repo thực hành `toolshop-practice` của em: một bạn gõ, một bạn đọc phiếu và soát. Xong mỗi bài thì đổi vai. Bài B3.3 làm theo nhóm 3 người nếu có thể.

Mục tiêu cuối buổi: `pytest tests/buoi3 -v` ra `6 passed`, và repo của em có một lượt CI xanh trên 3 trình duyệt.

Lý thuyết của từng bài nằm trong bài đọc `bai-doc/buoi-3-bdd-va-ci.md`, số mục ghi ở đầu mỗi bài.

## 0. Chuẩn bị (4 phút)

1. Mở VS Code, mở thư mục `toolshop-practice`, mở terminal, bật môi trường ảo (`.venv\Scripts\activate` trên Windows, `source .venv/bin/activate` trên macOS / Linux).
2. Lấy bài giải buổi 1 nếu chưa có (bài BDD dùng page object buổi 1):

   ```bash
   git fetch lop
   git checkout lop/bai-giai -- pages tests/buoi1/test_b1_pom.py
   ```

3. Kiểm tra 2 thứ cho phần CI:

   ```bash
   ls toolshop                  # phải thấy docker-compose.yml  nginx.conf  start.sh
   git config user.name         # phải ra tên em
   ```

   - Không có thư mục `toolshop`: `git checkout lop/main -- toolshop .github/workflows/ci.yml.todo`
   - `git config user.name` trống: `git config --global user.name "Tên Em"` và `git config --global user.email "email-github-cua-em"`

4. Chạy thử: `pytest tests/buoi3 -v`. Đúng: `4 failed`, mỗi test báo `StepDefinitionNotFoundError`.

### Các file của buổi

| File | Bài | Dòng (file gốc) |
|---|---|---|
| `tests/buoi3/test_b3_bdd.py` | B3.2, B3.4 | TODO B3.2 ở dòng 41 - 42; `scenarios(...)` ở dòng 16; gợi ý B3.4 ở dòng 45 - 49 |
| `tests/buoi3/features/cart.feature` | B3.3 | Cả file là chú thích yêu cầu (dòng 1 - 12), em viết đè |
| `.github/workflows/ci.yml.todo` | B3.5 | TODO ở dòng 6, 21, 23, 45 - 47, 51, 53 |

### Luật buổi này

1. Step chỉ gọi page object. Thấy cần `page.get_by_test_id(...)` trong step thì locator đó còn thiếu trong `pages/`.
2. Câu Gherkin nói về nghiệp vụ, không nói về nút bấm, data-test hay CSS.
3. Không commit `test-results/`, `report.html`, `.env`.

---

## Phần A - BDD với pytest-bdd

### B3.1 - Chạy và đọc (cùng giảng viên, 3 phút, bài đọc mục 0.3 và 2)

```bash
pytest tests/buoi3 -v
```

Đọc output và trả lời:

1. Có mấy test? Vì sao 1 file feature sinh ra ngần ấy test? (Đếm số dòng `Examples` cộng số `Scenario`.)
2. Mở `tests/buoi3/features/search.feature`. Dòng lỗi `Line 11` chỉ câu nào?
3. Hai câu nào chưa có step definition?

### B3.2 - Viết 2 step còn thiếu (8 phút, bài đọc mục 3.2)

**Mở:** `tests/buoi3/test_b3_bdd.py`, dòng 41 - 42:

```python
# TODO: @then('the search caption mentions "{keyword}"')
# TODO: @then('I see the message "{message}"')
```

**Làm từng bước:** xoá 2 dòng TODO, viết 2 step, mỗi step 3 dòng:

1. Dòng decorator: `@then(parsers.parse('the search caption mentions "{keyword}"'))`. Nhớ `parsers.parse` vì câu có giá trị thay đổi.
2. Dòng `def`: tên hàm tuỳ em, tham số là `home` (fixture từ bước Given) và `keyword`.
3. Thân hàm: kiểm `home.search_caption` có chứa `keyword` (`to_contain_text`).
4. Làm tương tự cho câu `I see the message "{message}"`: kiểm `home.no_results` có chữ `message` (`to_have_text`).

**Chạy:** `pytest tests/buoi3 -v`

**Đạt khi:** `4 passed`.

<details><summary>Gợi ý</summary>

```python
@then(parsers.parse('the search caption mentions "{keyword}"'))
def caption_mentions(home, keyword):
    expect(home.search_caption).to_contain_text(keyword)
```

Viết step mà vẫn báo `StepDefinitionNotFoundError`: thiếu `parsers.parse`, hoặc chữ trong step khác chữ trong feature.

</details>

### B3.3 - Three Amigos: viết cart.feature (8 phút, bài đọc mục 1 - 2)

Chia vai trong nhóm: **Product Owner** đọc quy tắc nghiệp vụ và giữ đúng nghĩa; **Dev** hỏi "đo bằng gì?"; **Tester** hỏi "còn trường hợp nào?".

**Mở:** `tests/buoi3/features/cart.feature`. Đọc 12 dòng chú thích (quy tắc nghiệp vụ và yêu cầu), rồi xoá hết, viết feature:

1. Dòng `Feature: Shopping cart` và câu chuyện 3 dòng `As a ... / I want ... / So that ...`.
2. `Background:` với bước `Given I am on the home page` (đã có step, dùng lại).
3. Một `Scenario Outline` có các bước theo thứ tự: mở sản phẩm, thêm vào giỏ với số lượng, mở giỏ hàng, giỏ có đúng sản phẩm, giá dòng bằng đơn giá nhân số lượng, tổng giỏ bằng tổng các dòng.
4. Bảng `Examples` cột `| product | quantity |`, 2 dòng: `Combination Pliers` / `1` và `Claw Hammer` / `3`.

**Tự soát:**

- Có đủ câu chuyện 3 dòng.
- `Scenario Outline` có bảng `Examples` (quên bảng thì test chạy với chữ `<product>` nguyên văn và đỏ sau 30 giây).
- Không câu nào nhắc nút, data-test, CSS.

Chưa chạy được ở bước này: phải thêm file vào `scenarios(...)` ở B3.4.

### B3.4 - Step cho giỏ hàng (12 phút, bài đọc mục 3.3)

1. **Dòng 16:** `scenarios("search.feature")` thành `scenarios("search.feature", "cart.feature")`. Chỉ ghi tên file, không ghi đường dẫn.
2. Chạy `pytest tests/buoi3 -v`: thấy 2 test mới đỏ `StepDefinitionNotFoundError`, chỉ đúng câu đầu tiên chưa có step.
3. Viết step **ở cuối file** (dưới dòng gợi ý 45 - 49), từng câu một, chạy lại sau mỗi step:

| Câu (trong feature của em) | Step trả về / kiểm gì | `target_fixture` |
|---|---|---|
| `When I open the product "<product>"` | Trả về `home.open_product(product)` | `product_page` |
| `And I add it to the cart with quantity <quantity>` | Đọc `product_page.price()` **trước**, rồi `add_to_cart(quantity=quantity)`, chờ badge giỏ hàng đúng số lượng, trả về đơn giá | `unit_price` |
| `And I open the cart` | Trả về `product_page.go_to_cart()` | `cart` |
| `Then the cart contains "<product>"` | Giỏ có đúng 1 dòng, tên đúng sản phẩm | |
| `And the line price equals the unit price times <quantity>` | `cart.line_totals()[0]` bằng `unit_price * quantity` (dùng `pytest.approx`) | |
| `And the cart total equals the sum of the line prices` | `cart.total_value()` bằng tổng `cart.line_totals()` | |

Số trong câu dùng `{quantity:d}` để nhận số nguyên.

**Đạt khi:** `pytest tests/buoi3 -v` ra `6 passed`: 4 test tìm kiếm, `[Combination Pliers-1]`, `[Claw Hammer-3]`.

<details><summary>Gợi ý</summary>

```python
@when(parsers.parse('I open the product "{product}"'), target_fixture="product_page")
def open_product(home, product):
    return home.open_product(product)


@when(parsers.parse("I add it to the cart with quantity {quantity:d}"), target_fixture="unit_price")
def add_to_cart(product_page, quantity):
    unit = product_page.price()          # đọc giá trước khi thêm
    product_page.add_to_cart(quantity=quantity)
    expect(product_page.cart_quantity).to_have_text(str(quantity))
    return unit
```

- `fixture 'product_page' not found`: bước trước quên `target_fixture="product_page"`.
- `TypeError: can't multiply sequence by non-int of type 'float'`: thiếu `:d`, `quantity` là chuỗi.
- Vẫn chỉ 4 test: chưa thêm `"cart.feature"` vào `scenarios(...)`.

</details>

---

## Phần B - GitHub Actions

### B3.5 - Điền ci.yml (8 phút, bài đọc mục 4.2 - 4.3)

**Mở:** `.github/workflows/ci.yml.todo`. Điền 6 TODO. Mỗi TODO trả lời được câu "vì sao":

| Dòng | TODO | Điền | Câu hỏi |
|---|---|---|---|
| 6 | `on:` | 3 trigger: `push` (nhánh `main`), `pull_request`, `workflow_dispatch` | Khi nào `workflow_dispatch` có ích? |
| 21 | `fail-fast:` | `false` | Firefox đỏ thì có nên huỷ WebKit đang chạy không? |
| 23 | `browser:` | `[chromium, firefox, webkit]` | |
| 45 - 47 | lệnh pytest | `pytest -m smoke --browser ${{ matrix.browser }} -n 2 --reruns 1 --tracing retain-on-failure --screenshot only-on-failure --html=report.html --self-contained-html` | Vì sao `-n 2` mà không `-n auto`? Vì sao chỉ `--reruns 1`? |
| 51 | `if:` | `always()` | Khi test đỏ, có cần báo cáo không? |
| 53 | `name:` | `report-${{ matrix.browser }}` | 3 trình duyệt cùng tên `report` thì sao? |

Dòng 11 `BASE_URL: http://localhost:4200` có sẵn: vì sao CI không test thẳng vào practicesoftwaretesting.com? (bài đọc mục 4.3)

Thụt lề bằng **2 dấu cách**, thẳng cột với dòng mẫu, không dùng phím Tab. Lệnh pytest dài viết nhiều dòng sau `run: >` (xem bài đọc mục 4.2).

Xong thì **đổi tên tệp thành `ci.yml`** (bỏ `.todo`): trong VS Code bấm chuột phải vào tệp, **Rename**. Còn đuôi `.todo` thì GitHub không chạy.

<details><summary>Gợi ý</summary>

```yaml
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:
```

```yaml
        run: >
          pytest -m smoke --browser ${{ matrix.browser }}
          -n 2 --reruns 1
          --tracing retain-on-failure --screenshot only-on-failure
          --html=report.html --self-contained-html
```

</details>

### B3.6 - Đẩy lên và xem chạy (5 phút, bài đọc mục 4.4)

```bash
git add .github/workflows/
git commit -m "Add CI workflow for three browsers"
git push
```

Mở repo trên GitHub, tab **Actions**. Thấy lượt chạy tên "Add CI workflow for three browsers", 3 job chạy song song.

**Đạt khi:** 3 job xanh. Đo thật ngày 17/11: mỗi job khoảng 1,5 - 2,5 phút, bước Run tests in `2 passed`.

Trong lúc chờ, làm B3.7 bước 1 (bật luật cần lượt chạy này xong mới chọn được status check).

### B3.7 - Bảo vệ main và phá build qua Pull Request (10 phút, bài đọc mục 5)

1. **Bật luật:** Settings → **Branches** → **Add classic branch protection rule**. Branch name pattern `main`. Tích **Require a pull request before merging**. Tích **Require status checks to pass before merging**, ô tìm gõ `test`, chọn cả 3 `test (chromium)`, `test (firefox)`, `test (webkit)`. Bấm **Create**.
2. **Phá build trên nhánh mới:**

   ```bash
   git switch -c feature/break-build
   ```

   Mở `tests/buoi1/test_b1_pom.py`, **Ctrl+F** tìm `to_contain_text("pliers")` (dòng 29, hoặc dòng 30 nếu đã lấy bài giải buổi 1). Đổi `"pliers"` thành `"plierz"`. Ctrl+S.

   ```bash
   git commit -am "Break the build on purpose"
   git push -u origin feature/break-build
   ```

3. Trên GitHub bấm **Compare & pull request**, **Create pull request**.
4. **Quan sát:** CI chạy lại với sự kiện `pull_request`, cả 3 job đỏ, nút **Merge pull request** bị khoá.
5. **Sửa lại:** đổi `"plierz"` về `"pliers"`, rồi:

   ```bash
   git commit -am "Fix the assertion"
   git push
   ```

   CI chạy lại, xanh, bấm **Merge pull request**.

### B3.8 - Đọc bằng chứng của lượt đỏ (8 phút, bài đọc mục 6)

1. Tab Actions, mở lượt chạy đỏ của bước B3.7, bấm job `test (chromium)`, mở bước **Run tests**, đọc dòng lỗi.
2. Quay lại trang **Summary** của lượt chạy, kéo xuống **Artifacts**, tải `report-chromium`.
3. Giải nén **ra ngoài thư mục repo** (ví dụ thư mục Downloads). Mở `report.html` bằng trình duyệt.
4. Trong thư mục `test-results/` có một thư mục cho test đỏ. Mở trace:

   ```bash
   playwright show-trace <đường-dẫn>/test-results/<thư-mục-của-test>/trace.zip
   ```

   Bấm vào bước đỏ (dòng `expect ... to_contain_text`), xem trang lúc đó: chữ trên trang là "pliers", test chờ "plierz".
5. Thêm badge vào cuối `README.md` (đổi `<tài-khoản>` thành tên GitHub của em), commit qua một nhánh và Pull Request như bước B3.7:

   ```markdown
   ![CI](https://github.com/<tài-khoản>/toolshop-practice/actions/workflows/ci.yml/badge.svg)
   ```

---

## Kiểm tra cuối buổi

```bash
pytest tests/buoi3 -v                    # 6 passed
git ls-files .github/workflows           # chỉ có .github/workflows/ci.yml
grep -rn "get_by_\|locator(" tests/buoi3 # không in gì
git ls-files | grep -E "test-results|\.venv|__pycache__|report.*html"   # không in gì
```

Windows PowerShell thay 2 lệnh `grep`: `Select-String -Path tests\buoi3\*.py -Pattern "get_by_|locator\("` và `git ls-files | Select-String "test-results|\.venv|__pycache__|report.*html"`.

---

## Bài về nhà = nửa sau Sprint 2 đồ án (nghiệm thu đầu buổi 25/11)

Hướng dẫn từng bước: `docs/sprint-2b.md` trong repo lớp.

1. 1 feature BDD trong repo nhóm: `Scenario Outline` + `Examples`, step gọi page object (đề mục 3.7).
2. `ci.yml` trong repo nhóm đầy đủ đề mục 3.9 - 3.10: 3 trình duyệt xanh, artifact riêng từng trình duyệt.
3. `main` của repo nhóm bắt buộc Pull Request có review và 3 status check xanh.
4. README có badge CI, ảnh lượt CI xanh và ảnh Trace Viewer.
5. `git ls-files | grep -E "test-results|\.venv|__pycache__|report.*html"` không in gì.

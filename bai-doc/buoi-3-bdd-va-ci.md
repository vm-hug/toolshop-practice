# Bài đọc buổi 3 - BDD với pytest-bdd, CI với GitHub Actions

Buổi học ngày 18/11. Đọc lại sau buổi khoảng 35 phút. Code BDD đã chạy thật trên Toolshop; workflow CI đã chạy thật trên GitHub Actions ngày 17/11/2026.

Sau bài này, em làm được:

1. Viết file `.feature` bằng Gherkin, có `Scenario Outline` và `Examples`.
2. Viết step definition bằng pytest-bdd, gọi lại page object, chuyền dữ liệu giữa các bước bằng `target_fixture`.
3. Nói được BDD mang lại gì và tốn gì.
4. Viết workflow GitHub Actions chạy 3 trình duyệt, giữ lại báo cáo và trace.
5. Bảo vệ nhánh `main` để Pull Request đỏ không merge được, rồi đọc bằng chứng của lượt chạy đỏ.

## 0. Chuẩn bị và cách chạy

### 0.1 Kiểm tra trước khi vào bài

```bash
git fetch lop
git checkout lop/bai-giai -- pages tests/buoi1/test_b1_pom.py   # nếu chưa lấy bài giải buổi 1
ls toolshop                                                      # phải thấy docker-compose.yml, nginx.conf, start.sh
git config user.name                                             # phải ra tên em
```

- Bài BDD dùng `HomePage`, `ProductPage`, `CartPage` của buổi 1, nên cần bài giải buổi 1 (README mục 6).
- Thư mục `toolshop/` dựng Toolshop bằng Docker cho CI. Repo tạo rất sớm (sáng 02/11) có thể chưa có; thiếu thì lấy bù: `git checkout lop/main -- toolshop .github/workflows/ci.yml.todo`.
- `git config user.name` trống thì đặt: `git config --global user.name "Tên Em"` và `git config --global user.email "email@github"`.

### 0.2 Các file của buổi

| File | Bài |
|---|---|
| `tests/buoi3/features/search.feature` | Feature có sẵn: tìm kiếm |
| `tests/buoi3/features/cart.feature` | B3.3: em tự viết (file chỉ có chú thích yêu cầu) |
| `tests/buoi3/test_b3_bdd.py` | B3.2, B3.4: step definition |
| `.github/workflows/ci.yml.todo` | B3.5: điền TODO rồi đổi tên thành `ci.yml` |

### 0.3 Chạy và đọc kết quả

```bash
pytest tests/buoi3 -v
```

Chạy lần đầu, trước khi làm gì: `4 failed`. Mỗi dòng của bảng `Examples` thành một test riêng, tên có giá trị trong ngoặc: `test_search_returns_only_matching_products[pliers]`.

Cả 4 test đỏ cùng một kiểu lỗi:

```
E   pytest_bdd.exceptions.StepDefinitionNotFoundError: Step definition is not found:
    Then "the search caption mentions "pliers"". Line 11 in scenario "Search returns only matching products"
```

pytest-bdd chỉ đúng **câu Gherkin nào** chưa có code, ở **dòng nào** của file feature. Đây là cách làm việc của buổi này: viết feature trước, chạy, rồi viết từng step theo danh sách lỗi.

## 1. Vì sao có BDD

Câu yêu cầu "Đơn hàng trên 100 đô được giảm giá" có thể được hiểu ba kiểu:

- Product Owner: từ 100 đô trở lên, giảm 10% trên tổng trước thuế.
- Lập trình viên: lớn hơn 100, giảm 10 đô, tính sau thuế.
- Tester: đúng 100 thì sao? Có mã giảm giá khác thì cộng dồn không?

BDD (Behavior-Driven Development) là thói quen viết kịch bản bằng ngôn ngữ chung **trước** khi code, để ba vai trên hiểu giống nhau. Buổi họp ba vai cùng viết kịch bản gọi là **Three Amigos**: Product Owner giữ quy tắc nghiệp vụ, Dev hỏi "đo bằng gì?", Tester hỏi "còn trường hợp nào?".

## 2. Gherkin

`tests/buoi3/features/search.feature` (có sẵn):

```gherkin
Feature: Product search
  As a shopper
  I want to search products by name
  So that I find the tool I need quickly

  Background:
    Given I am on the home page

  Scenario Outline: Search returns only matching products
    When I search for "<keyword>"
    Then the search caption mentions "<keyword>"
    And every product name contains "<keyword>"

    Examples:
      | keyword |
      | pliers  |
      | hammer  |
      | saw     |

  Scenario: Search with an unknown word shows the empty state
    When I search for "zzz-no-such-tool"
    Then I see the message "There are no products found."
```

| Từ khoá | Ý nghĩa |
|---|---|
| `Feature` | Chức năng, kèm câu chuyện người dùng 3 dòng: As a, I want, So that |
| `Background` | Các bước chạy trước mọi kịch bản trong file |
| `Scenario` | Một kịch bản cụ thể |
| `Scenario Outline` + `Examples` | Một kịch bản chạy nhiều lần, mỗi dòng bảng một lần. `<keyword>` được thay bằng giá trị trong bảng |
| `Given` | Trạng thái ban đầu |
| `When` | Hành động của người dùng |
| `Then` | Kết quả quan sát được |
| `And` | Thêm một bước cùng loại với bước trước |

File trên sinh ra 4 test: 3 dòng `Examples` của kịch bản đầu, cộng 1 kịch bản thường.

### Viết Gherkin tốt

1. Câu nói về nghiệp vụ, không nói về giao diện. Sai: `When I click the button with data-test search-submit`. Đúng: `When I search for "saw"`.
2. Mỗi kịch bản một hành vi, khoảng 3 đến 7 bước.
3. `Then` mô tả thứ người dùng thấy được, đủ cụ thể để kiểm.
4. `Scenario Outline` luôn đi kèm `Examples`. Quên bảng thì kịch bản vẫn chạy, nhưng với chữ `<product>` nguyên văn, và đỏ sau 30 giây vì không tìm thấy sản phẩm nào tên `<product>`.

## 3. pytest-bdd

### 3.1 Từ câu Gherkin tới page object

```
search.feature           When I search for "saw"
       |
step definition          @when(parsers.parse('I search for "{keyword}"'))
       |
page object              home.search(keyword)
```

Step chỉ gọi page object và kiểm kết quả. Nếu thấy mình cần viết `page.get_by_test_id(...)` trong step, locator đó đang thiếu trong `pages/`. pytest không báo lỗi vi phạm này; người review Pull Request phải bắt.

### 3.2 Step definition

`tests/buoi3/test_b3_bdd.py` (phần có sẵn):

```python
pytestmark = [pytest.mark.bdd, pytest.mark.ui]

# Đường dẫn tính từ bdd_features_base_dir trong pytest.ini (tests/buoi3/features)
scenarios("search.feature")


@given("I am on the home page", target_fixture="home")
def home(page):
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    return home


@when(parsers.parse('I search for "{keyword}"'))
def search(home, keyword):
    home.search(keyword)


@then(parsers.parse('every product name contains "{keyword}"'))
def names_contain(home, keyword):
    expect(home.search_completed).to_be_visible()
    names = home.product_names.all_inner_texts()
    assert names and all(keyword.lower() in n.lower() for n in names), names
```

| Thành phần | Tác dụng |
|---|---|
| `scenarios("search.feature")` | Sinh một test pytest cho mỗi kịch bản, mỗi dòng Examples |
| `@given`, `@when`, `@then` | Gắn hàm với một câu Gherkin |
| `parsers.parse('... "{keyword}"')` | Lấy giá trị trong câu ra thành tham số `keyword` |
| `{quantity:d}` | Lấy ra số nguyên. Thiếu `:d` thì nhận được chuỗi `"3"` |
| `target_fixture="home"` | Giá trị hàm trả về thành fixture tên `home` cho các bước sau |

Hai điều hay nhầm:

- **Câu có giá trị thay đổi phải dùng `parsers.parse`.** Viết `@then('the search caption mentions "{keyword}"')` không có `parsers.parse` thì pytest-bdd tìm đúng câu có chữ `{keyword}` nguyên văn, và vẫn báo `StepDefinitionNotFoundError`.
- **Câu trong step phải khớp từng chữ với câu trong feature.** Feature viết `I add it to cart` (thiếu `the`) thì không khớp step `I add it to the cart`: lỗi chỉ đúng câu đó.

### 3.3 Chuyền dữ liệu giữa các bước: `target_fixture`

Kịch bản giỏ hàng cần mở sản phẩm ở bước này, thêm vào giỏ ở bước sau, rồi so giá ở bước cuối. Mỗi bước trả về thứ bước sau cần, đặt tên bằng `target_fixture`:

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

`open_product` trả về ProductPage với tên `product_page`; `add_to_cart` nhận `product_page` làm tham số. Quên `target_fixture="product_page"` thì bước sau báo `fixture 'product_page' not found`.

Quên `:d` ở `{quantity:d}` thì `quantity` là chuỗi `"3"`, và phép `unit_price * quantity` báo `TypeError: can't multiply sequence by non-int of type 'float'`.

### 3.4 Được gì, mất gì

| Được | Mất |
|---|---|
| Product Owner đọc hiểu được kịch bản | Thêm một tầng gián tiếp giữa yêu cầu và code |
| Tài liệu luôn đúng, vì nó chạy được | Kho step phình to, khó tìm, dễ trùng |
| Một kịch bản, nhiều dòng dữ liệu | Dễ biến thành "Gherkin hoá từng cú click", vô nghĩa với người đọc |

Đồ án yêu cầu một luồng nghiệp vụ viết BDD (đề mục 3.7). Phần còn lại viết pytest thường.

## 4. CI với GitHub Actions

### 4.1 Khái niệm

| Thuật ngữ | Nghĩa |
|---|---|
| Workflow | Một file YAML trong `.github/workflows/`, mô tả việc tự động |
| Trigger | Sự kiện kích hoạt: push, pull request, bấm tay |
| Job | Một nhóm bước chạy trên một máy |
| Step | Một lệnh hoặc một action có sẵn |
| Runner | Máy ảo của GitHub chạy job, ví dụ `ubuntu-latest` |
| Matrix | Chạy cùng một job với nhiều cấu hình, ví dụ 3 trình duyệt |
| Artifact | File giữ lại sau khi chạy: báo cáo, trace, ảnh chụp |

### 4.2 Workflow của buổi này

`.github/workflows/ci.yml` sau khi điền TODO (bài B3.5):

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

env:
  BASE_URL: http://localhost:4200      # Toolshop tự dựng trong job, xem mục 4.3
  API_URL: http://localhost:8091
  GITHUB_API_URL: https://api.github.com
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

jobs:
  test:
    name: test (${{ matrix.browser }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        browser: [chromium, firefox, webkit]
    steps:
      - uses: actions/checkout@v4

      - name: Start Toolshop containers
        run: docker compose -f toolshop/docker-compose.yml up -d

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Install browser
        run: playwright install --with-deps ${{ matrix.browser }}

      - name: Wait for Toolshop and load seed data
        run: bash toolshop/start.sh

      - name: Run tests
        run: >
          pytest -m smoke --browser ${{ matrix.browser }}
          -n 2 --reruns 1
          --tracing retain-on-failure --screenshot only-on-failure
          --html=report.html --self-contained-html

      - name: Upload report and traces
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: report-${{ matrix.browser }}
          path: |
            report.html
            test-results/
          retention-days: 7
```

Mỗi dòng quan trọng và lý do:

| Dòng | Vì sao |
|---|---|
| 3 trigger trong `on:` | Chạy khi vào `main`, trên mọi Pull Request, và bấm tay (nút **Run workflow**) khi cần chạy lại |
| `env: BASE_URL, API_URL` | URL nằm ở cấu hình, không nằm trong code. Cùng bộ test chạy trên site công khai ở máy em và trên Toolshop tự dựng ở CI |
| `docker compose ... up -d` | Khởi động Toolshop riêng của job ngay từ đầu, để giao diện biên dịch trong lúc job cài Python và trình duyệt |
| `bash toolshop/start.sh` | Nạp dữ liệu mẫu và chờ tới khi UI, API trả lời. Chạy test trước lúc này thì đỏ hàng loạt |
| `GITHUB_TOKEN` | GitHub tự cấp token cho mỗi lượt chạy, để test GitHub API không bị chặn vì hết lượt |
| `fail-fast: false` | Firefox đỏ không huỷ WebKit đang chạy, giữ đủ thông tin để chẩn đoán |
| `--with-deps` | Cài thư viện hệ thống. Thiếu thì WebKit không chạy |
| `-m smoke` | Bắt đầu với nhóm test nhanh để CI xanh ngay. Repo thực hành còn bài buổi 4 chưa làm, chạy cả bộ thì đỏ vì `NotImplementedError` |
| `-n 2` | Chạy 2 test song song, vừa sức máy của GitHub |
| `--reruns 1` | Chịu được một lần lỗi mạng. Không đặt cao hơn để che test sai |
| `--tracing retain-on-failure`, `--screenshot only-on-failure` | Chỉ giữ bằng chứng của test đỏ, artifact gọn |
| `if: always()` | Bước sau mặc định bị bỏ khi bước trước đỏ, mà test đỏ là lúc cần báo cáo nhất |
| `name: report-${{ matrix.browser }}` | Ba job cùng tên `report` thì bước upload báo lỗi trùng tên |
| `retention-days: 7` | Không giữ artifact quá lâu |

### 4.3 Vì sao CI tự dựng Toolshop

Site công khai practicesoftwaretesting.com đứng sau Cloudflare. Cloudflare coi trình duyệt không giao diện chạy từ máy chủ của GitHub là bot và trả về trang "Performing security verification" thay cho Toolshop. Thử chạy trên site công khai ngày 02/11, 41/59 test Chromium đỏ vì trang này. Ở máy em thì không sao.

Doanh nghiệp cũng làm vậy: CI không test vào hệ thống dùng chung mà tự dựng một môi trường test riêng cho mỗi lượt chạy. Được ba điều:

1. Không bị chặn, không phụ thuộc site công khai có sống hay không.
2. Dữ liệu sạch mỗi lần: tài khoản mẫu không bị ai khoá, giỏ hàng không bị ai thêm đồ.
3. Kết quả lặp lại được: đỏ là do code, không phải do mạng.

Thư mục `toolshop/` lo việc này bằng Docker image chính chủ của Testsmith: `sprint5` là PROD, `sprint5-with-bugs` là BUGGY. Em không cần sửa gì trong đó. Testsmith chỉ cho dùng nội bộ, phi thương mại: không mở Toolshop tự dựng ra Internet.

### 4.4 Đẩy lên và xem chạy

```bash
git add .github/workflows/
git commit -m "Add CI workflow for three browsers"
git push
```

`git add .github/workflows/` (cả thư mục) để git ghi nhận cả việc xoá `ci.yml.todo` lẫn thêm `ci.yml`.

Mở tab **Actions** của repo: thấy lượt chạy tên đúng câu commit, 3 job `test (chromium)`, `test (firefox)`, `test (webkit)` chạy song song. Bấm vào một job để xem từng bước.

## 5. Bảo vệ `main` và Pull Request

### 5.1 Bật luật

Settings, **Branches**, **Add classic branch protection rule**, Branch name pattern `main`:

1. Tích **Require a pull request before merging**.
2. Tích **Require status checks to pass before merging**, ô tìm kiếm gõ `test`, chọn cả 3: `test (chromium)`, `test (firefox)`, `test (webkit)`.
3. Bấm **Create**.

Ô tìm ở bước 2 chỉ hiện tên job **sau khi workflow đã chạy ít nhất một lần**. Không thấy thì quay lại tab Actions chờ lượt chạy đầu xong.

### 5.2 Luồng làm việc qua Pull Request

```bash
git switch -c feature/<tên>-<việc>
# sửa code, chạy pytest ở máy
git add . && git commit -m "Add CartPage and line price test"
git push -u origin feature/<tên>-<việc>
```

Trên GitHub bấm **Compare & pull request**. Lượt chạy CI mới mở ra với sự kiện `pull_request`. Còn check đỏ thì nút Merge bị khoá. Sửa, đẩy thêm commit lên cùng nhánh, CI chạy lại, xanh thì merge.

Từ khi bật luật, `git push` thẳng lên `main` bị từ chối: đúng như mong muốn.

## 6. Đọc bằng chứng của lượt chạy đỏ

1. Tab Actions, mở lượt chạy đỏ, xem job nào đỏ, bấm bước **Run tests** đọc lỗi.
2. Kéo xuống cuối trang **Summary**, phần **Artifacts**, tải `report-<trình duyệt>` (file zip).
3. Giải nén, mở `report.html` bằng trình duyệt: test nào đỏ, thông báo lỗi.
4. Trong `test-results/` mỗi test đỏ có một thư mục riêng chứa `trace.zip`. Mở bằng:

   ```bash
   playwright show-trace test-results/<thư-mục-của-test>/trace.zip
   ```

5. Trace Viewer cho xem từng bước: ảnh DOM trước và sau, request mạng, console. Bấm vào bước đỏ để xem trang lúc đó.

Test API (không mở trình duyệt) không có trace; xem thông báo lỗi trong `report.html`.

Badge CI cho README:

```markdown
![CI](https://github.com/<tài-khoản>/<repo>/actions/workflows/ci.yml/badge.svg)
```

## 7. Không commit rác

`.gitignore` của repo đã có:

```
__pycache__/
.venv/
.pytest_cache/
test-results/
report*.html
.env
```

Kiểm tra: `git ls-files | grep -E "test-results|\.venv|__pycache__|report.*html"` phải không in gì. Đề trừ 0,5 điểm nếu commit các thư mục này. Artifact tải về để ngoài repo, không giải nén vào thư mục repo.

## 8. Lỗi thường gặp

| Pytest hoặc GitHub báo | Nguyên nhân | Sửa |
|---|---|---|
| `StepDefinitionNotFoundError: Step definition is not found: Then "..."` | Câu chưa có step, hoặc chữ trong feature và step không khớp | Viết step, hoặc sửa cho khớp từng chữ |
| Vẫn `StepDefinitionNotFoundError` dù đã viết step | Quên `parsers.parse` cho câu có `{...}` | `@then(parsers.parse('...'))` |
| `fixture 'product_page' not found` | Bước trước quên `target_fixture` | `target_fixture="product_page"` |
| `fixture 'home' not found` | Kịch bản thiếu bước `Given I am on the home page` | Thêm `Background` hoặc bước `Given` |
| `TypeError: can't multiply sequence by non-int of type 'float'` | Thiếu `:d`, `quantity` là chuỗi | `{quantity:d}` |
| Viết `cart.feature` xong mà vẫn chỉ 4 test | Chưa thêm `"cart.feature"` vào `scenarios(...)` | `scenarios("search.feature", "cart.feature")` |
| `FileNotFoundError: ... features/tests/buoi3/features/cart.feature` | Ghi cả đường dẫn trong `scenarios(...)` | Chỉ ghi tên file, đường dẫn đã có trong `pytest.ini` |
| Kịch bản đỏ vì không tìm thấy sản phẩm `<product>` | `Scenario Outline` thiếu `Examples` | Thêm bảng `Examples` |
| Tab Actions không có lượt chạy nào | File vẫn tên `ci.yml.todo`, hoặc chưa push | Đổi tên thành `ci.yml`, `git add .github/workflows/`, push |
| Tab Actions báo lỗi cú pháp YAML | Thụt lề sai (dùng Tab, lệch cột) | Thụt bằng 2 dấu cách, thẳng cột với dòng mẫu |
| `upload-artifact` báo trùng tên | 3 job cùng `name: report` | `report-${{ matrix.browser }}` |
| WebKit đỏ hết từ đầu | Thiếu `--with-deps` | `playwright install --with-deps ...` |
| CI đỏ vì `NotImplementedError` | Chạy cả bộ thay vì `-m smoke` | Thêm `-m smoke` |
| `git push` bị từ chối (protected branch) | Đã bảo vệ `main` | Đi qua nhánh và Pull Request |
| Không chọn được status check khi bật luật | Workflow chưa chạy lần nào | Chờ lượt chạy đầu xong |

## 9. Đếm lại và tự kiểm tra

Cuối buổi:

```bash
pytest tests/buoi3 -v                    # 6 passed: 4 tìm kiếm, 2 giỏ hàng
git ls-files .github/workflows           # .github/workflows/ci.yml (không còn .todo)
grep -rn "get_by_\|locator(" tests/buoi3 # không in gì: step không chứa locator
```

Trên GitHub: tab Actions có một lượt chạy xanh (3 job) và một lượt chạy đỏ của Pull Request phá build, đã sửa xanh và merge.

Câu hỏi tự kiểm tra:

1. `Scenario Outline` khác `Scenario` ở đâu? File `search.feature` sinh ra mấy test?
2. `target_fixture` dùng để làm gì? Cho một ví dụ trên Toolshop.
3. Vì sao step definition không nên chứa locator mới?
4. Vì sao đồ án cần `fail-fast: false` và tên artifact riêng cho từng trình duyệt?
5. Bỏ `if: always()` ở bước upload thì chuyện gì xảy ra khi có test đỏ?
6. Vì sao CI không test thẳng vào practicesoftwaretesting.com?
7. Một test chỉ đỏ trên WebKit. Em sẽ mở những gì, theo thứ tự nào?

## 10. Liên hệ đồ án

- Đề mục 3.7 BDD, 3.8 Git và GitHub, 3.9 GitHub Actions, 3.10 Báo cáo và artifact.
- Câu vấn đáp 9, 12, 13.
- Bài về nhà (nửa sau Sprint 2, nghiệm thu 25/11): `docs/sprint-2b.md` trong repo lớp.

## 11. Đọc thêm

- pytest-bdd: https://pytest-bdd.readthedocs.io/
- Gherkin: https://cucumber.io/docs/gherkin/reference/
- GitHub Actions: https://docs.github.com/en/actions
- Bảo vệ nhánh: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- Playwright trên CI: https://playwright.dev/python/docs/ci
- Trace Viewer: https://playwright.dev/python/docs/trace-viewer

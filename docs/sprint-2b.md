# Sprint 2, nửa sau (hạn: đầu buổi 25/11)

Nửa đầu Sprint 2 (`docs/sprint-2.md`) đã có test API, route, data-driven và test giao diện. Nửa sau đưa vào repo nhóm 2 thứ học ở buổi 3: một feature BDD và CI chạy 3 trình duyệt.

Cần nộp cho 25/11:

1. **1 feature BDD** (đề mục 3.7): một luồng nghiệp vụ, có `Scenario Outline` + `Examples`, step definition bằng pytest-bdd gọi lại page object.
2. **`ci.yml` đầy đủ** (đề mục 3.9 - 3.10): 3 trigger, ma trận Chromium / Firefox / WebKit, `fail-fast: false`, báo cáo HTML và trace, artifact riêng từng trình duyệt.
3. **`main` được bảo vệ**: bắt buộc Pull Request có 1 người duyệt và 3 status check xanh.
4. **README** có badge CI, ảnh một lượt CI xanh và ảnh Trace Viewer.
5. **Không commit rác**: `git ls-files | grep -E "test-results|\.venv|__pycache__|report.*html"` không in gì.

Làm trong repo nhóm, trên một nhánh mới:

```bash
git checkout main
git pull
git checkout -b feature/<tên-em>-sprint2b
```

## Bước 1. Feature BDD

### 1.1 Chọn luồng và viết feature

Gợi ý luồng: tìm sản phẩm → thêm vào giỏ → giỏ tính đúng tiền. Nhóm tự chọn luồng khác cũng được, miễn là một luồng nghiệp vụ, không phải một trang.

Tạo `tests/bdd/features/<tên-luồng>.feature`, theo mẫu `cart.feature` của buổi 3:

- `Feature` có câu chuyện 3 dòng `As a / I want / So that`.
- Ít nhất 1 `Scenario Outline` với bảng `Examples` từ 2 dòng.
- Câu nói về nghiệp vụ, không nói về nút, data-test, CSS.

### 1.2 Sửa `pytest.ini` cho đúng thư mục feature

`pytest.ini` chép từ repo thực hành có dòng:

```ini
bdd_features_base_dir = tests/buoi3/features
```

Repo nhóm để feature ở `tests/bdd/features`, nên sửa thành:

```ini
bdd_features_base_dir = tests/bdd/features
```

Quên sửa thì `scenarios(...)` báo `FileNotFoundError` và cả file step không chạy.

### 1.3 Viết step definition

Tạo `tests/bdd/test_<tên-luồng>.py` (tên phải bắt đầu bằng `test_`, nếu không pytest bỏ qua):

```python
import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from pages.home_page import HomePage

pytestmark = [pytest.mark.bdd, pytest.mark.ui]

scenarios("<tên-luồng>.feature")
```

Rồi chạy `pytest tests/bdd -v`, viết từng step theo lỗi `StepDefinitionNotFoundError` như buổi 3. Step chỉ gọi page object; locator mới thêm vào `pages/`.

**Đạt khi:** `pytest tests/bdd -v` xanh, mỗi dòng `Examples` là một test.

## Bước 2. CI cho repo nhóm

### 2.1 Chép 2 thứ từ repo thực hành

| Chép | Vào repo nhóm |
|---|---|
| Thư mục `toolshop/` (3 file) | `toolshop/` |
| `.github/workflows/ci.yml` (bản em đã điền ở B3.5) | `.github/workflows/ci.yml` |

`toolshop/` dựng Toolshop bằng Docker trong mỗi job CI, vì site công khai chặn trình duyệt chạy trên máy GitHub. Không cần sửa gì trong đó.

### 2.2 Bỏ `-m smoke`

Bản B3.5 chạy `pytest -m smoke` vì repo thực hành còn bài chưa làm. Repo nhóm phải chạy **cả bộ test**, nên bỏ `-m smoke` ở bước Run tests:

```yaml
      - name: Run tests
        run: >
          pytest --browser ${{ matrix.browser }}
          -n 2 --reruns 1
          --tracing retain-on-failure --screenshot only-on-failure
          --html=report.html --self-contained-html
```

Đối chiếu đề mục 3.9 - 3.10:

| Đề yêu cầu | Dòng trong `ci.yml` |
|---|---|
| Kích hoạt khi push main, pull request, workflow_dispatch | `on:` có 3 trigger |
| Ma trận Chromium / Firefox / WebKit trên ubuntu-latest, `fail-fast: false` | `strategy:` |
| Checkout → Python → thư viện → playwright install --with-deps → pytest → upload artifact | Các bước theo đúng thứ tự (thêm 2 bước Toolshop) |
| pytest-html `--self-contained-html`, luôn upload `if: always()` | Bước Run tests và Upload |
| Trace và screenshot khi có test lỗi | `--tracing retain-on-failure --screenshot only-on-failure` |
| Tên artifact riêng từng trình duyệt, retention ngắn | `name: report-${{ matrix.browser }}`, `retention-days: 7` |
| pytest-rerunfailures trong CI, giới hạn số tiến trình (đề mục 3.11) | `--reruns 1`, `-n 2` |

### 2.3 Chạy ở máy trước, rồi mở Pull Request

```bash
pytest                                   # cả bộ phải xanh ở máy (site công khai)
git add toolshop .github tests pages pytest.ini
git status                               # KHÔNG được thấy .env, test-results/, report.html
git commit -m "Add BDD feature and CI workflow"
git push -u origin feature/<tên-em>-sprint2b
```

Mở Pull Request. CI chạy với sự kiện `pull_request`. Đỏ thì tải artifact, mở `report.html` và trace (bài đọc buổi 3 mục 6), sửa, đẩy thêm commit. Xanh và có người duyệt thì merge.

Test xanh ở máy mà đỏ trên CI: CI dùng Toolshop tự dựng, dữ liệu mới mỗi lần. Hay gặp là test phụ thuộc dữ liệu có sẵn trên site công khai (ví dụ một tài khoản ai đó đã tạo) hoặc assert số lượng tuyệt đối. Sửa test để tự tạo dữ liệu của mình.

## Bước 3. Bảo vệ `main`

Sau khi CI đã chạy ít nhất một lần, trưởng nhóm vào **Settings → Branches**, sửa luật của `main` (đã tạo ở Sprint 1):

- **Require a pull request before merging**, **Require approvals**: 1 (đã có từ Sprint 1).
- Tích thêm **Require status checks to pass before merging**, chọn `test (chromium)`, `test (firefox)`, `test (webkit)`.
- Bấm **Save changes**.

## Bước 4. README

Thêm vào `README.md` của repo nhóm (qua một Pull Request):

```markdown
![CI](https://github.com/<trưởng-nhóm>/<tên-repo>/actions/workflows/ci.yml/badge.svg)

## Kết quả CI

![CI xanh](docs/screenshots/ci-green.png)

## Trace Viewer

![Trace Viewer](docs/screenshots/trace-viewer.png)
```

- `ci-green.png`: chụp trang lượt chạy CI xanh, thấy cả 3 job.
- `trace-viewer.png`: chụp Trace Viewer mở trace của một test đỏ (ví dụ lượt đỏ khi đang sửa), thấy bước đỏ và ảnh trang.

Lưu ảnh vào `docs/screenshots/` (đề mục 4).

## Bước 5. Kiểm tra trước khi nộp

```bash
pytest tests/bdd -v                      # xanh
git ls-files | grep -E "test-results|\.venv|__pycache__|report.*html"   # không in gì
grep -rn "get_by_\|locator(" tests/      # không in gì
```

Windows PowerShell: `git ls-files | Select-String "test-results|\.venv|__pycache__|report.*html"` và `Select-String -Path tests\*\*.py -Pattern "get_by_|locator\("`.

## Nghiệm thu đầu buổi 25/11 (mỗi nhóm 1 phút)

Một bạn chiếu màn hình:

1. Tab **Actions**: lượt chạy mới nhất trên `main` xanh cả 3 job.
2. README: badge CI xanh, 2 ảnh.
3. **Settings → Branches**: luật của `main` có 3 status check.
4. Terminal: `pytest tests/bdd -v` xanh.

Kẹt ở bước nào: chụp màn hình lỗi (cả lệnh đã gõ) gửi lên nhóm lớp.

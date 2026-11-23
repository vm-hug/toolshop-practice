"""Buoi 2 - route / mocking, and API + UI together.

Run:  pytest tests/buoi2/test_b2_network.py --headed
"""
import json
import re

import pytest  # noqa: F401
from playwright.sync_api import expect

from pages.account_page import AccountPage  # noqa: F401
from pages.home_page import HomePage  # noqa: F401

# Open DevTools > Network on the home page and look at how the product list is loaded:
#   PROD:   QUERY https://api.practicesoftwaretesting.com/products          (JSON body)
#   BUGGY:  GET   https://api-with-bugs.../products?between=price,1&page=1
# One regex catches both, and NOT /products/search or /products/{id}:
PRODUCT_LIST = re.compile(r"/products(\?.*)?$")
EMPTY_PAGE = {"current_page": 1, "data": [], "from": None, "last_page": 1,
              "per_page": 9, "to": None, "total": 0}


# ---------------------------------------------------------------- B2.7
def test_b2_7_home_without_images_still_lists_products(page):
    """Goal: kiểm tra trang hoạt động khi ảnh bị chặn.
    Precondition: đăng ký route chặn ảnh trước khi mở trang.
    Expected: tên sản phẩm vẫn hiện và có yêu cầu ảnh bị chặn."""
    blocked = []

    def block(route):
        blocked.append(route.request.url)
        route.abort()

    image_pattern = re.compile(
        r"\.(png|jpe?g|webp|avif|svg)(\?.*)?$",
        re.IGNORECASE,
    )
    page.route(image_pattern, block)
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()

    assert blocked, "Không có yêu cầu ảnh nào bị chặn"


# ---------------------------------------------------------------- B2.8
def test_b2_8_home_with_empty_product_list_shows_no_results(page):
    """Goal: kiểm tra giao diện khi danh sách sản phẩm rỗng.
    Precondition: API danh sách trả về EMPTY_PAGE.
    Expected: hiện thông báo không tìm thấy và không có sản phẩm."""
    mocked = []

    def empty_products(route):
        mocked.append(route.request.url)
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(EMPTY_PAGE),
        )

    page.route(PRODUCT_LIST, empty_products)
    home = HomePage(page).open()
    expect(home.no_results).to_have_text(
        "There are no products found."
    )
    expect(home.product_names).to_have_count(0)

    assert mocked, "Route giả lập danh sách rỗng chưa chạy"


# ---------------------------------------------------------------- B2.9
def test_b2_9_home_when_product_api_fails_page_stays_usable(page):
    """Goal: kiểm tra trang vẫn thao tác được khi API sản phẩm lỗi.
    Precondition: API danh sách trả về HTTP 500.
    Expected: không có sản phẩm, ô tìm kiếm vẫn nhập được."""
    mocked = []

    def server_error(route):
        mocked.append(route.request.url)
        route.fulfill(
            status=500,
            content_type="application/json",
            body=json.dumps({
                "message": "Internal Server Error",
            }),
        )

    page.route(PRODUCT_LIST, server_error)
    home = HomePage(page).open()
    expect(home.search_box).to_be_visible()
    expect(home.search_box).to_be_editable()

    home.search_box.fill("pliers")

    expect(home.search_box).to_have_value("pliers")
    expect(home.product_names).to_have_count(0)

    assert mocked, "Route giả lập lỗi 500 chưa chạy"


# ---------------------------------------------------------------- B2.10 (challenge)
def test_b2_10_home_renders_price_from_api_response(page):
    """Goal: kiểm tra giao diện hiển thị giá từ API.
    Precondition: sửa giá sản phẩm đầu tiên trong phản hồi thành 999.99.
    Expected: giá đầu tiên trên giao diện là $999.99."""
    patched = []

    def patch_price(route):
        response = route.fetch()

        assert response.status == 200, response.text()

        body = response.json()

        assert body["data"], "Không có sản phẩm để sửa giá"

        body["data"][0]["price"] = 999.99
        patched.append(route.request.url)

        route.fulfill(
            response=response,
            json=body,
        )
    page.route(PRODUCT_LIST, patch_price)
    home = HomePage(page).open()
    expect(home.product_prices.first).to_have_text("$999.99")

    assert patched, "Route sửa giá chưa chạy"


# ---------------------------------------------------------------- B2.11 (challenge)
def test_b2_11_account_page_with_token_injected_skips_login_form(
    page,
    auth_token,
):
    """Goal: mở trang tài khoản mà không thao tác form đăng nhập.
    Precondition: fixture cung cấp token của tài khoản riêng.
    Expected: hiện My account và tên QA Bot trên menu."""
    page.add_init_script(
        "window.localStorage.setItem("
        f"'auth-token', {json.dumps(auth_token)}"
        ")"
    )
    account = AccountPage(page).open()

    expect(account.title).to_have_text("My account")
    expect(account.nav_menu).to_contain_text("QA Bot")


# ---------------------------------------------------------------- B2.12 (given): storage state, login once per session
def test_b2_12_logged_in_page_shows_user_menu(logged_in_page):
    """Goal: reuse a saved login (fixture auth_state in conftest.py). Precondition: none.
    Expected: user menu shows the account name."""
    account = AccountPage(logged_in_page).open()
    expect(account.title).to_have_text("My account")
    expect(account.nav_menu).to_contain_text("QA Bot")

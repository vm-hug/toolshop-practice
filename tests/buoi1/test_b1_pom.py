"""Buoi 1 - Page Object Model exercises. Turn every red test green.

Run one exercise:   pytest tests/buoi1 -k b1_1 --headed --slowmo 300
Run all of buoi 1:  pytest tests/buoi1

Rules (same as the final project):
- No locator in this file: locators live in pages/.
- No assertion in pages/: assertions live here.
- No time.sleep(), no wait_for_timeout().
- Every test has a 3-line docstring: goal, precondition, expected.
"""
import re

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.login_page import LoginPage


# ---------------------------------------------------------------- B1.1 (together with the teacher)
@pytest.mark.smoke
@pytest.mark.ui
def test_b1_1_search_keyword_shows_only_matching_products(page):
    """Goal: search filters the grid.
    Precondition: none.
    Expected: caption shows the keyword and every product name contains it."""
    home = HomePage(page).open().search("pliers")
    expect(home.search_completed).to_be_visible()
    expect(home.search_caption).to_contain_text("plierz")
    names = home.product_names.all_inner_texts()
    assert names, "search returned no products"
    assert all("pliers" in n.lower() for n in names), names


# ---------------------------------------------------------------- B1.2
def test_b1_2_search_unknown_keyword_shows_no_results_message(page):
    """Goal: kiểm tra tìm kiếm không có kết quả.
    Precondition: mở trang chủ.
    Expected: hiện thông báo không tìm thấy và không có sản phẩm."""
    home = HomePage(page).open().search("zzz-no-such-tool")

    expect(home.search_completed).to_be_visible()
    expect(home.no_results).to_have_text("There are no products found.")
    expect(home.product_names).to_have_count(0)


# ---------------------------------------------------------------- B1.3
def test_b1_3_product_add_quantity_three_updates_cart_badge(page):
    """Goal: kiểm tra thêm sản phẩm theo số lượng đã chọn.
    Precondition: sản phẩm Claw Hammer tồn tại, giỏ hàng trống.
    Expected: hiện toast thành công và badge giỏ hàng bằng 3."""
    product = HomePage(page).open().open_product("Claw Hammer")

    expect(product.name).to_contain_text("Claw Hammer")

    product.add_to_cart(quantity=3)

    expect(product.toast).to_contain_text("Product added to shopping cart")
    expect(product.cart_quantity).to_have_text("3")


# ---------------------------------------------------------------- B1.4
def test_b1_4_cart_line_price_equals_unit_price_times_quantity(page):
    """Goal: kiểm tra thành tiền và tổng giỏ hàng.
    Precondition: giỏ hàng trống, sản phẩm Combination Pliers tồn tại.
    Expected: thành tiền bằng đơn giá nhân 2, tổng bằng tổng các dòng."""
    product = HomePage(page).open().open_product("Combination Pliers")

    expect(product.name).to_contain_text("Combination Pliers")
    expect(product.unit_price).to_be_visible()

    unit = product.price()

    product.add_to_cart(quantity=2)
    expect(product.cart_quantity).to_have_text("2")

    cart = product.go_to_cart()

    expect(cart.product_titles).to_have_count(1)
    expect(cart.product_titles.first).to_have_text("Combination Pliers")
    expect(cart.quantities.first).to_have_value("2")
    expect(cart.line_prices.first).to_be_visible()
    expect(cart.total).to_be_visible()

    line_totals = cart.line_totals()

    assert line_totals == pytest.approx([unit * 2])
    assert cart.total_value() == pytest.approx(sum(line_totals))


# ---------------------------------------------------------------- B1.5
def test_b1_5_login_wrong_password_shows_error(page):
    """Goal: kiểm tra từ chối thông tin đăng nhập sai.
    Precondition: dùng email không tồn tại, không dùng tài khoản chung.
    Expected: hiện lỗi và vẫn ở trang đăng nhập."""
    login_page = LoginPage(page).open()

    login_page.login(
        "nobody-here@example.com",
        "Wrong-Password-123",
    )

    expect(login_page.error).to_contain_text("Invalid email or password")
    expect(page).to_have_url(re.compile(r"/auth/login$"))


def test_b1_5_login_empty_form_shows_required_errors(page):
    """Goal: kiểm tra các trường bắt buộc của form đăng nhập.
    Precondition: chưa nhập email và mật khẩu.
    Expected: hiện Email is required và Password is required."""
    login_page = LoginPage(page).open()

    login_page.submit_button.click()

    expect(login_page.email_error).to_have_text("Email is required")
    expect(login_page.password_error).to_have_text("Password is required")


# ---------------------------------------------------------------- B1.6
def test_b1_6_cart_continue_shopping_returns_to_home(page):
    """Goal: kiểm tra quay lại trang chủ từ giỏ hàng.
    Precondition: sản phẩm Hammer tồn tại và giỏ hàng ban đầu trống.
    Expected: giỏ có Hammer, bấm Continue Shopping hiện lại sản phẩm."""
    cart = (
        HomePage(page)
        .open()
        .open_product("Hammer")
        .add_to_cart()
        .go_to_cart()
    )

    expect(cart.product_titles).to_have_count(1)
    expect(cart.product_titles.first).to_have_text("Hammer")
    expect(cart.cart_quantity).to_have_text("1")

    cart.continue_shopping.click()

    home = HomePage(page)
    expect(home.product_names.first).to_be_visible()


# ---------------------------------------------------------------- B1.7 (challenge)
@pytest.mark.parametrize("order", ["price,asc", "price,desc"])
def test_b1_7_sort_by_price_orders_products(page, order):
    """Goal: kiểm tra sắp xếp sản phẩm theo giá.
    Precondition: trang chủ có sản phẩm.
    Expected: giá tăng dần hoặc giảm dần theo lựa chọn."""
    home = HomePage(page).open().sort_by(order)

    expect(home.sorting_completed).to_be_visible()
    expect(home.product_prices.first).to_be_visible()

    prices = home.prices()

    assert len(prices) >= 2, "Cần ít nhất hai sản phẩm để kiểm tra thứ tự giá"

    expected_prices = sorted(
        prices,
        reverse=(order == "price,desc"),
    )

    assert prices == expected_prices

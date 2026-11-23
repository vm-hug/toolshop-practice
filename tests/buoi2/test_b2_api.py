"""Buoi 2 - API testing with APIRequestContext (not the requests library).

Fixtures you can use (see conftest.py): api, test_user, auth_token, auth_headers
Helpers: register_user(api, email, password), new_email(), strong_password()

Run:  pytest tests/buoi2/test_b2_api.py -v
"""
import json
from pathlib import Path

import pytest

from conftest import new_email, register_user, strong_password  # noqa: F401  (you will need them)

KEYWORDS = json.loads((Path(__file__).parents[2] / "data" / "search_keywords.json").read_text())


# ---------------------------------------------------------------- B2.1 (together)
@pytest.mark.smoke
@pytest.mark.api
def test_b2_1_status_returns_toolshop(api):
    """Goal: API is alive. Precondition: none. Expected: 200 and app_name Toolshop."""
    response = api.get("/status")
    assert response.status == 200, response.text()
    assert response.json()["app_name"] == "Toolshop"


# ---------------------------------------------------------------- B2.2
def test_b2_2_products_first_page_has_pagination_and_product_shape(api):
    """Goal: kiểm tra cấu trúc phản hồi danh sách sản phẩm.
    Precondition: API hoạt động và có sản phẩm.
    Expected: đủ khóa phân trang, sản phẩm có id, tên và giá hợp lệ."""
    response = api.get("/products", params={"page": 1})

    assert response.status == 200, response.text()

    body = response.json()

    assert isinstance(body, dict), body

    for key in (
        "current_page",
        "data",
        "per_page",
        "total",
        "last_page",
    ):
        assert key in body, f"Thiếu khóa {key}: {body}"

    assert isinstance(body["data"], list), body
    assert isinstance(body["per_page"], int), body
    assert 0 < len(body["data"]) <= body["per_page"], body

    for product in body["data"]:
        assert isinstance(product["id"], (str, int)), product

        assert (
            isinstance(product["name"], str)
            and product["name"].strip()
        ), product

        assert (
            isinstance(product["price"], (int, float))
            and product["price"] > 0
        ), product


# ---------------------------------------------------------------- B2.3 data-driven
@pytest.mark.parametrize(
    "case",
    KEYWORDS,
    ids=[case["keyword"] for case in KEYWORDS],
)
def test_b2_3_search_api_returns_only_matching_names(api, case):
    """Goal: kiểm tra tìm kiếm API với dữ liệu từ JSON.
    Precondition: từ khóa trong dữ liệu có sản phẩm phù hợp.
    Expected: có kết quả và mọi tên đều chứa chuỗi yêu cầu."""
    response = api.get(
        "/products/search",
        params={"q": case["keyword"]},
    )

    assert response.status == 200, response.text()

    names = [
        product["name"]
        for product in response.json()["data"]
    ]

    assert names, f"Không có kết quả cho {case['keyword']}"

    assert all(
        case["must_contain"].lower() in name.lower()
        for name in names
    ), names


# ---------------------------------------------------------------- B2.4 errors
# B2.4a: one parametrized test: GET /users/me -> 401, GET /products/does-not-exist -> 404
@pytest.mark.parametrize(
    "path, expected",
    [
        ("/users/me", 401),
        ("/products/does-not-exist", 404),
    ],
)
def test_b2_4a_protected_or_missing_resource_returns_4xx(
    api,
    path,
    expected,
):
    """Goal: kiểm tra mã lỗi cho yêu cầu không hợp lệ.
    Precondition: không gửi token hoặc yêu cầu sản phẩm không tồn tại.
    Expected: trả về mã 401 hoặc 404 tương ứng."""
    response = api.get(path)
    assert response.status == expected, response.text()


def test_b2_4b_register_empty_body_returns_422_with_field_errors(api):
    """Goal: kiểm tra xác thực dữ liệu đăng ký ở server.
    Precondition: gửi biểu mẫu đăng ký rỗng.
    Expected: trả về 422 và lỗi cho email, password."""
    response = api.post("/users/register", data={})
    assert response.status == 422, response.text()
    errors = response.json()

    assert "email" in errors, errors
    assert "password" in errors, errors


def test_b2_4c_register_leaked_password_is_rejected(api):
    """Goal: kiểm tra chính sách từ chối mật khẩu từng bị lộ.
    Precondition: đăng ký email mới với mật khẩu Welcome01!.
    Expected: trả về 422 và có lỗi password."""
    response = register_user(
        api,
        new_email(),
        "Welcome01!",
    )
    assert response.status == 422, response.text()
    errors = response.json()

    assert "password" in errors, errors


# ---------------------------------------------------------------- B2.5 token
def test_b2_5a_users_me_with_token_returns_own_profile(
    api,
    auth_headers,
    test_user,
):
    """Goal: kiểm tra token cho phép truy cập hồ sơ.
    Precondition: fixture đã tạo tài khoản và lấy token.
    Expected: trả về 200 và email đúng tài khoản đã tạo."""
    response = api.get(
        "/users/me",
        headers=auth_headers,
    )
    assert response.status == 200, response.text()
    body = response.json()

    assert body["email"] == test_user["email"], body


def test_b2_5b_register_response_does_not_expose_password(api):
    """Goal: kiểm tra phản hồi đăng ký không lộ mật khẩu.
    Precondition: email mới và mật khẩu ngẫu nhiên đủ mạnh.
    Expected: tạo thành công với mã 201, JSON không có khóa password."""
    response = register_user(
        api,
        new_email(),
        strong_password(),
    )
    assert response.status == 201, response.text()
    body = response.json()

    assert "password" not in body, "Phản hồi đăng ký chứa khóa password"


# ---------------------------------------------------------------- B2.6 your own fixture
@pytest.fixture
def new_cart(api):
    """Tạo giỏ hàng riêng cho mỗi test sử dụng fixture."""
    response = api.post("/carts")

    assert response.status == 201, response.text()

    return response.json()["id"]


# B2.6: write a fixture `new_cart` (in this file) that POSTs /carts and returns the id.
def test_b2_6_cart_add_product_quantity_two_is_stored(
    api,
    new_cart,
):
    """Goal: kiểm tra API lưu đúng sản phẩm và số lượng.
    Precondition: giỏ hàng mới và danh sách có sản phẩm.
    Expected: giỏ có đúng một dòng, số lượng 2, đúng product_id."""
    products_response = api.get(
        "/products",
        params={"page": 1},
    )

    assert products_response.status == 200, products_response.text()

    products = products_response.json()["data"]

    assert products, "API không trả về sản phẩm"

    product = products[0]

    added_response = api.post(
        f"/carts/{new_cart}",
        data={
            "product_id": product["id"],
            "quantity": 2,
        },
    )

    assert added_response.ok, added_response.text()

    cart_response = api.get(f"/carts/{new_cart}")

    assert cart_response.status == 200, cart_response.text()

    items = cart_response.json()["cart_items"]

    assert len(items) == 1, items
    assert items[0]["quantity"] == 2, items
    assert str(items[0]["product_id"]) == str(product["id"]), items

from pages.base_page import BasePage


def money(text: str) -> float:
    """Chuyển chuỗi tiền, ví dụ '$28.30', thành số 28.3."""
    return float(text.replace("$", "").replace(",", "").strip())


class CartPage(BasePage):
    path = "/checkout"

    def __init__(self, page):
        super().__init__(page)

        # B1.4: product_titles, quantities, line_prices, total
        self.product_titles = page.get_by_test_id("product-title")
        self.quantities = page.get_by_test_id("product-quantity")
        self.line_prices = page.get_by_test_id("line-price")
        self.total = page.get_by_test_id("cart-total")

        # B1.6: continue_shopping
        self.continue_shopping = page.get_by_test_id("continue-shopping")

    def line_totals(self) -> list[float]:
        # B1.4
        return [
            money(text)
            for text in self.line_prices.all_inner_texts()
        ]

    def total_value(self) -> float:
        # B1.4
        return money(self.total.inner_text())

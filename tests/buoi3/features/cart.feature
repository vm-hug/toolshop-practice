# B3.3 - write this feature yourself (Gherkin), then add "cart.feature" to scenarios(...) in test_b3_bdd.py
#
# Business rule to describe:
#   When a shopper adds a product with a quantity, the cart line price is unit price x quantity,
#   and the cart total is the sum of the line prices.
#
# Requirements:
#   - Feature with a 3-line user story (As a / I want / So that)
#   - One Scenario Outline with an Examples table of at least 2 rows: | product | quantity |
#     suggested rows: Combination Pliers / 1 and Claw Hammer / 3
#   - Steps speak business language ("I add it to the cart with quantity 3"),
#     never UI language ("I click the button with data-test add-to-cart").

Feature: Shopping cart
  As a shopper
  I want to add products with a chosen quantity
  So that I can review the correct amount before checkout

  Background:
    Given I am on the home page

  Scenario Outline: Cart prices match the selected product and quantity
    When I open the product "<product>"
    And I add it to the cart with quantity <quantity>
    And I open the cart
    Then the cart contains "<product>"
    And the line price equals the unit price times <quantity>
    And the cart total equals the sum of the line prices

    Examples:
      | product            | quantity |
      | Combination Pliers | 1        |
      | Claw Hammer        | 3        |
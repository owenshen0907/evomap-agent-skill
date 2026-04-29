"""Checkout pricing helpers.

Amounts are integer cents. Coupon percent is a user-entered integer.
"""


def price_after_coupon_cents(subtotal_cents: int, coupon_percent: int) -> int:
    """Return subtotal after a percentage coupon.

    BUG: this version truncates fractional cents, allows negative coupon
    values, and can return a negative total when coupon_percent > 100.
    """
    discount = int(subtotal_cents * coupon_percent / 100)
    return subtotal_cents - discount

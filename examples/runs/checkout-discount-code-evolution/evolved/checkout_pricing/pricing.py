"""Checkout pricing helpers.

Amounts are integer cents. Coupon percent is a user-entered integer.
"""

from decimal import Decimal, ROUND_HALF_UP


def price_after_coupon_cents(subtotal_cents: int, coupon_percent: int) -> int:
    """Return subtotal after a percentage coupon.

    The function validates unsafe inputs, clamps over-100% coupons to a free
    order, and rounds the discount to the nearest cent with half-up semantics.
    """
    if not isinstance(subtotal_cents, int) or not isinstance(coupon_percent, int):
        raise TypeError("subtotal_cents and coupon_percent must be integers")
    if subtotal_cents < 0:
        raise ValueError("subtotal_cents cannot be negative")
    if coupon_percent < 0:
        raise ValueError("coupon_percent cannot be negative")

    bounded_percent = min(coupon_percent, 100)
    discount = (
        Decimal(subtotal_cents) * Decimal(bounded_percent) / Decimal(100)
    ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return max(0, subtotal_cents - int(discount))

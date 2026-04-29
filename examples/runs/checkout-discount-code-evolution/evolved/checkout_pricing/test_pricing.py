import unittest

from pricing import price_after_coupon_cents


class PriceAfterCouponTests(unittest.TestCase):
    def test_rounds_half_up_to_nearest_cent(self):
        # 15% of 333 cents is 49.95, so the discount should be 50 cents.
        self.assertEqual(price_after_coupon_cents(333, 15), 283)

    def test_coupon_over_100_percent_cannot_create_negative_total(self):
        self.assertEqual(price_after_coupon_cents(999, 125), 0)

    def test_negative_coupon_is_rejected(self):
        with self.assertRaises(ValueError):
            price_after_coupon_cents(999, -10)

    def test_negative_subtotal_is_rejected(self):
        with self.assertRaises(ValueError):
            price_after_coupon_cents(-1, 10)

    def test_full_discount_is_zero(self):
        self.assertEqual(price_after_coupon_cents(2500, 100), 0)


if __name__ == "__main__":
    unittest.main()

"""Illustrative revenue arithmetic, with no predicted time horizon."""

from decimal import Decimal


def revenue_with_one_order(order_values):
    """Add one hypothetical order to imported revenue.

    Values must be in newest-first order, as returned by the Shopify sync.
    The hypothetical order equals the mean of up to three latest orders.
    This is neither a time-series forecast nor evidence of expected growth.
    """
    values = [Decimal(str(value)) for value in order_values]
    if any(not value.is_finite() for value in values):
        raise ValueError("Order values must be finite.")
    total = sum(values, Decimal("0"))
    recent = values[:3]
    return total + sum(recent, Decimal("0")) / len(recent) if recent else total

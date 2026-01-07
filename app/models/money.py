"""Monetary types and utilities for the application"""

from __future__ import annotations

import decimal
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from pydantic_core import core_schema


class Money(Decimal):
    """Custom Money type based on Decimal for precise financial calculations.
    Always rounds to 2 decimal places and provides monetary operations.

    Usage:
        # Creating Money instances
        price = Money("99.99")
        fee = Money(2.5)  # Will be rounded to 2.50

        # Arithmetic operations
        total = price + fee  # Returns Money instance

        # Comparisons
        if price.is_positive():
            print("Price is positive")
    """

    def __new__(cls, value="0.00"):
        if isinstance(value, str):
            if not value or value.strip() == "":
                value = "0.00"
        elif value is None:
            value = "0.00"

        try:
            decimal_value = Decimal(str(value))
        except (ValueError, decimal.InvalidOperation):
            raise ValueError(f"Invalid monetary value: {value!r}. Must be a number or numeric string.")

        # Support Infinity and NaN: do not quantize these special values
        if decimal_value.is_infinite() or decimal_value.is_nan():
            return super().__new__(cls, decimal_value)

        rounded_value = decimal_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return super().__new__(cls, rounded_value)

    def __str__(self):
        """Return string representation with 2 decimal places or 'Infinity'/'-Infinity' for special values."""
        if self.is_infinite():
            return "Infinity" if self > 0 else "-Infinity"
        if self.is_nan():
            return "NaN"
        return f"{self:.2f}"

    def __repr__(self):
        return f"Money('{self}')"

    def to_float(self) -> float:
        """Convert to float (use with caution in calculations)"""
        return float(self)

    def to_string(self) -> str:
        """Convert to string with 2 decimal places"""
        return str(self)

    def is_zero(self) -> bool:
        """Check if amount is zero (Infinity/NaN is never zero)"""
        return not (self.is_infinite() or self.is_nan()) and self == Decimal("0.00")

    def is_positive(self) -> bool:
        """Check if amount is positive (Infinity is positive)"""
        return self > Decimal("0.00")

    def is_negative(self) -> bool:
        """Check if amount is negative (Negative Infinity is negative)"""
        return self < Decimal("0.00")

    def abs(self) -> Money:
        """Return absolute value as Money"""
        return Money(abs(self))

    def round_to_cents(self) -> Money:
        """Explicitly round to 2 decimal places (already done in __new__)"""
        return self

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> core_schema.CoreSchema:
        """
        Return a Pydantic CoreSchema that validates the Money type.
        This allows Pydantic to understand how to serialize/deserialize Money.
        Money will be serialized as float for JSON compatibility.
        """
        return core_schema.no_info_plain_validator_function(
            cls,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: float(x),  # Serialize as float for JSON
                return_schema=core_schema.float_schema(),
            ),
        )

    @classmethod
    def create(cls, value) -> Money:
        """Helper function to create Money instances"""
        return cls(value)

    @classmethod
    def format_currency(cls, amount: Money, currency: str) -> str:
        """Format money amount with currency symbol"""
        symbols = {
            "USD": "$",
            "NGN": "₦",
            "EUR": "€",
            "GBP": "£",
        }
        symbol = symbols.get(currency, currency)
        return f"{symbol}{amount:,.2f}"

    @classmethod
    def calculate_fee_percentage(cls, amount: Money, percentage: float) -> Money:
        """Calculate percentage-based fee"""
        fee = amount * Decimal(str(percentage / 100))
        return cls(fee)

    @classmethod
    def calculate_fee_fixed(cls, fee_amount: Money) -> Money:
        """Calculate fixed fee (returns the fee amount)"""
        return cls(fee_amount)

    @classmethod
    def sum_money(cls, *amounts: Money) -> Money:
        """Sum multiple Money amounts"""
        return cls(sum(amounts, cls("0.00")))

    @classmethod
    def max_money(cls, *amounts: Money) -> Money:
        """Return the maximum Money amount"""
        return cls(max(amounts))

    @classmethod
    def min_money(cls, *amounts: Money) -> Money:
        """Return the minimum Money amount"""
        return cls(min(amounts))

    def __add__(self, other) -> Money:
        """Override addition to ensure Money + Money returns Money"""
        return Money(super().__add__(Money(other)))

    def __sub__(self, other) -> Money:
        """Override subtraction to ensure Money - Money returns Money"""
        return Money(super().__sub__(Money(other)))

    def __mul__(self, other) -> Money:
        """Override multiplication to ensure Money * number returns Money"""
        return Money(super().__mul__(Decimal(str(other))))

    def __truediv__(self, other) -> Money:
        """Override division to ensure Money / number returns Money"""
        return Money(super().__truediv__(Decimal(str(other))))

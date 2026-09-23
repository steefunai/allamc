"""Reference implementation for backend/app/common/money.py (ADR-0003).

BOOT-001 copies this into app/common/money.py and grows it test-first. Integers only:
money = paise, rates = basis points (1800 = 18%), quantities = milli-units (1000 = 1 unit).
The built-in round() is banned in domain code (it rounds half to even); use these helpers.
"""
from __future__ import annotations

from dataclasses import dataclass

BP_DENOMINATOR = 10_000
MILLI = 1_000


def _require_int(*values: object) -> None:
    for v in values:
        # bool is a subclass of int; reject it too.
        if not isinstance(v, int) or isinstance(v, bool):
            raise TypeError(f"money helpers accept int only, got {type(v).__name__}")


def div_half_up(numerator: int, denominator: int) -> int:
    """Integer division rounding half away from zero."""
    _require_int(numerator, denominator)
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    sign = -1 if numerator < 0 else 1
    q, r = divmod(abs(numerator), denominator)
    if r * 2 >= denominator:
        q += 1
    return sign * q


def line_amount(unit_price_paise: int, qty_milli: int, discount_paise: int = 0) -> int:
    """Taxable value of a line: unit price x quantity, minus discount."""
    _require_int(unit_price_paise, qty_milli, discount_paise)
    gross = div_half_up(unit_price_paise * qty_milli, MILLI)
    if discount_paise < 0 or discount_paise > gross:
        raise ValueError("discount must be between 0 and the gross amount")
    return gross - discount_paise


def apply_rate(amount_paise: int, rate_bp: int) -> int:
    """amount x rate, half-up to the paisa (e.g. GST on a taxable value, renewal uplift)."""
    _require_int(amount_paise, rate_bp)
    return div_half_up(amount_paise * rate_bp, BP_DENOMINATOR)


@dataclass(frozen=True)
class GstSplit:
    cgst_paise: int
    sgst_paise: int
    igst_paise: int

    @property
    def total_paise(self) -> int:
        return self.cgst_paise + self.sgst_paise + self.igst_paise


def gst_for_line(taxable_paise: int, rate_bp: int, *, intra_state: bool) -> GstSplit:
    """Tax once per line, then split. Odd paisa goes to CGST (DATA-001 INV-07; CA to confirm)."""
    tax = apply_rate(taxable_paise, rate_bp)
    if not intra_state:
        return GstSplit(0, 0, tax)
    sgst = tax // 2
    return GstSplit(tax - sgst, sgst, 0)


def prorate(amount_paise: int, part_days: int, total_days: int) -> int:
    """Pro-rata charge/credit for amendments (D-21)."""
    _require_int(amount_paise, part_days, total_days)
    if not 0 <= part_days <= total_days or total_days <= 0:
        raise ValueError("invalid pro-rata period")
    return div_half_up(amount_paise * part_days, total_days)


def round_off_to_rupee(total_paise: int) -> tuple[int, int]:
    """Returns (rounded_total_paise, round_off_paise) for the optional invoice round-off line."""
    _require_int(total_paise)
    rounded = div_half_up(total_paise, 100) * 100
    return rounded, rounded - total_paise


def parse_rupees(text: str) -> int:
    """'1,234.5' -> 123450 paise. String arithmetic only; > 2 decimals rejected."""
    s = text.strip().replace(",", "")
    if s.startswith("-"):
        raise ValueError("negative amounts are not accepted here")
    whole, _, frac = s.partition(".")
    if not whole.isdigit() or (frac and (not frac.isdigit() or len(frac) > 2)):
        raise ValueError(f"invalid rupee amount: {text!r}")
    return int(whole) * 100 + int((frac + "00")[:2])

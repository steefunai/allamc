"""Starter tests for app/common/money.py — BOOT-001 moves these to backend/tests/unit/common/."""
import pytest
from app.common.money import (
    apply_rate, div_half_up, gst_for_line, line_amount, parse_rupees, prorate, round_off_to_rupee,
)

pytestmark = pytest.mark.unit

def test_half_up():
    assert div_half_up(5, 2) == 3 and div_half_up(-5, 2) == -3 and div_half_up(4, 3) == 1
def test_gst():
    s = gst_for_line(10001, 1800, intra_state=True)  # 1800.18 -> 1800
    assert s.total_paise == 1800 and s.cgst_paise == 900
    s = gst_for_line(10003, 1800, intra_state=True)  # 1800.54 -> 1801
    assert (s.cgst_paise, s.sgst_paise) == (901, 900)
    assert gst_for_line(10003, 1800, intra_state=False).igst_paise == 1801
def test_float_refused():
    with pytest.raises(TypeError): apply_rate(100.0, 1800)
    with pytest.raises(TypeError): apply_rate(True, 1800)
def test_line_and_parse():
    assert line_amount(12345, 1500) == 18518  # 18517.5 -> 18518
    assert parse_rupees("1,234.5") == 123450
    with pytest.raises(ValueError): parse_rupees("1.234")
def test_roundoff_prorate():
    assert round_off_to_rupee(123450) == (123500, 50)
    assert round_off_to_rupee(123449) == (123400, -49)
    assert prorate(365000, 100, 365) == 100000

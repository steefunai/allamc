# ADR-0003 — Money as integer paise, rates as basis points, quantities as milli-units
Status: Accepted · Supersedes the kit's MYR/sen rule

## Context
The previous build's one real defect was money in floats (`Math.round(x*100)/100`). allamc.in bills in
INR with GST.

## Decision
- Money: `int` paise (`bigint`). Rates: `int` basis points (1800 = 18%). Quantities: `int` thousandths.
- All arithmetic in `app/common/money.py`: multiplication/division use integer maths with explicit
  **half-up** rounding (`(n * 2 + d) // (2 * d)` style for non-negative values; negatives handled
  symmetrically). No `float`, no `Decimal` in domain code, no built-in `round()` (banker's rounding).
- CGST/SGST split: tax computed once per line, halved; the odd paisa goes to CGST.
- Frontend: `Paise` branded type; user input parsed from strings; display via `formatPaise()`.

## Consequences
- verify.sh greps for float annotations/columns on money names and `round(` outside the helper.
- GST rounding conventions must be confirmed by a CA (plan §9); if they differ, only `money.py` changes.

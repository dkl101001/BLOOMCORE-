# SPDX-License-Identifier: AGPL-3.0-only
# Authorship lineage: Frazer Σ Love ACO-Σ; Sara ΣΩ.
"""Decimal checks with no memory-dependent execution or invented facts."""
import csv
import io
import re
from decimal import Decimal, ROUND_HALF_UP

SCHEMAS = {
    "invoice": ["Item", "Qty", "Unit price", "Line total"],
    "inventory": ["Part", "Starting", "Used", "Remaining"],
    "tax": ["Expense", "Amount", "Tax rate", "Total"],
}
SAMPLES = {
    "invoice": [["Lab gloves", "3", "12.50", "37.50"], ["Cables", "4", "8.00", "36.00"], ["Labels", "2", "4.25", "8.50"]],
    "inventory": [["Connectors", "50", "12", "38"], ["Sensors", "20", "7", "14"], ["Adapters", "16", "5", "11"]],
    "tax": [["Parts", "80.00", "0.07", "85.60"], ["Shipping", "25.00", "0.00", "25.00"], ["Tools", "40.00", "0.07", "42.80"]],
}
CENT = Decimal("0.01")
NUMBER = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")


def validate_sheet(schema, rows):
    if schema not in SCHEMAS:
        raise ValueError("Choose invoice, inventory, or tax")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 2000:
        raise ValueError("A sheet requires 1–2000 rows")
    clean = []
    for row in rows:
        if not isinstance(row, list) or len(row) != 4 or any(not isinstance(x, str) or len(x) > 256 for x in row):
            raise ValueError("Each row needs four text cells, each at most 256 characters")
        clean.append([x.strip() for x in row])
    return clean


def parse_csv(text, schema):
    if schema not in SCHEMAS or not isinstance(text, str) or len(text.encode()) > 8*1024*1024:
        raise ValueError("Invalid CSV or schema")
    try:
        records = list(csv.reader(io.StringIO(text.lstrip("\ufeff")), strict=True))
    except csv.Error as e:
        raise ValueError("CSV quoting is malformed") from e
    if not records or records[0] != SCHEMAS[schema]:
        raise ValueError("CSV header must be: " + ",".join(SCHEMAS[schema]))
    return validate_sheet(schema, records[1:])


def export_csv(schema, rows):
    out = io.StringIO(newline="")
    writer = csv.writer(out); writer.writerow(SCHEMAS[schema])
    # Labels beginning with spreadsheet formula prefixes are escaped on export.
    safe = [[("'"+r[0]) if r[0].startswith(("=", "+", "-", "@", "\t", "\r")) else r[0], *r[1:]] for r in rows]
    # Malformed numerical inputs may be formulas too; preserve text safely.
    for r in safe:
        for j in (1, 2, 3):
            if not NUMBER.fullmatch(r[j]) and r[j].startswith(("=", "+", "-", "@", "\t", "\r")):
                r[j] = "'" + r[j]
    writer.writerows(safe)
    return out.getvalue()


def number(text):
    if not NUMBER.fullmatch(text) or len(text) > 32:
        return None
    n = Decimal(text)
    return n if abs(n) <= Decimal("1000000000") and max(0, -n.as_tuple().exponent) <= 8 else None


def audit(schema, rows):
    rows = validate_sheet(schema, rows); findings = []; names = {}; totals = Decimal(0)

    def add(i, j, kind, msg, fix=None, delta=Decimal(0), target=Decimal(0)):
        findings.append({"row": i, "col": j, "kind": kind, "message": msg, "fix": fix,
                         "delta": str(delta), "relative": str(min(Decimal(1), abs(delta)/max(Decimal(1),abs(target))))})

    for i, r in enumerate(rows):
        label = r[0].casefold()
        if not label:
            add(i, 0, "identity", f"Row {i+1} needs an item name; supply the real value.")
        elif label in names:
            add(i, 0, "identity", f"Row {i+1} repeats the name in row {names[label]+1}; check whether both are intended.")
        else:
            names[label] = i
        numbers = [number(x) for x in r[1:]]
        for j, n in enumerate(numbers, 1):
            if n is None:
                add(i, j, "format", f"{SCHEMAS[schema][j]} in row {i+1} needs a plain bounded number (≤8 decimal places).")
        if None in numbers:
            continue
        a, b, got = numbers
        valid = True
        if a < 0 or (schema != "tax" and a != a.to_integral()):
            add(i, 1, "range", f"Row {i+1}: the first input must be nonnegative" + (" and whole." if schema != "tax" else ".")); valid = False
        if b < 0 or (schema == "inventory" and (b != b.to_integral() or b > a)) or (schema == "tax" and b > 1):
            add(i, 2, "range", f"Row {i+1}: invalid {SCHEMAS[schema][2]}; " + {"inventory":"use whole stock values with Used ≤ Starting.","tax":"use a rate from 0 to 1.","invoice":"use a nonnegative price."}[schema]); valid = False
        if schema == "invoice" and b != b.quantize(CENT):
            add(i, 2, "range", f"Row {i+1}: unit price must have at most two decimal places."); valid = False
        if schema == "tax" and a != a.quantize(CENT):
            add(i, 1, "range", f"Row {i+1}: amount must have at most two decimal places."); valid = False
        if not valid:
            continue
        target = (a*b if schema == "invoice" else a-b if schema == "inventory" else a*(1+b)).quantize(CENT, rounding=ROUND_HALF_UP)
        totals += target
        # Compare exact inputs; do not hide extra fractions of a cent.
        if got != target:
            add(i, 3, "arithmetic", f"Row {i+1}: {SCHEMAS[schema][3]} should be {target:.2f}, not {r[3]}.", f"{target:.2f}", target-got, target)
    return {"findings": findings, "checked_rows": len(rows), "computed_total": f"{totals:.2f}",
            "total_scope": "valid-input rows only", "rounding": "Decimal ROUND_HALF_UP per row"}

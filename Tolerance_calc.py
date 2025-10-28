# Tolerance_calc.py
"""
Gauge GO / NO-GO Calculator (ISO Standard Based - Supports Multiple Tolerance Types)

This script calculates GO and NO-GO gauge values based on:
- Nominal size (mm)
- Tolerance expression type (±, +, -, ++, --, /)
It uses a hardcoded ISO tolerance table (T, Z, H/2 values in microns).
"""

from typing import Dict, Tuple, Optional

# ==============================
# ISO Table Data (Hardcoded)
# Includes T, Z, and H/2 values (all in microns)
# ==============================
ISO_TABLE: Dict[Tuple[float, float], Dict[str, list]] = {
    (0, 3): {
        "T":   [6, 10, 14, 25, 40, 60, 100, 140, 250, 400, 600],
        "Z":   [1, 1.5, 2, 5, 5, 10, 10, 20, 20, 40, 40],
        "H/2": [0.6, 1, 1, 1, 1, 2, 2, 5, 5, 5, 5]
    },
    (3, 6): {
        "T":   [8, 12, 18, 30, 48, 75, 120, 180, 300, 480, 750],
        "Z":   [1.5, 2, 3, 6, 6, 12, 12, 24, 24, 48, 48],
        "H/2": [0.75, 1.25, 1.25, 1.25, 1.25, 2.5, 2.5, 6, 6, 6, 6]
    },
    (6, 10): {
        "T":   [9, 15, 22, 36, 58, 90, 150, 220, 360, 580, 900],
        "Z":   [1.5, 2, 3, 7, 7, 14, 14, 28, 28, 56, 56],
        "H/2": [0.75, 1.25, 1.25, 1.25, 1.25, 3, 3, 7.5, 7.5, 7.5, 7.5]
    },
    (10, 18): {
        "T":   [11, 18, 27, 43, 70, 110, 180, 270, 430, 700, 1100],
        "Z":   [2, 2.5, 4, 8, 8, 16, 16, 32, 32, 64, 64],
        "H/2": [1, 1.5, 1.5, 1.5, 1.5, 4, 4, 9, 9, 9, 9]
    },
    (18, 30): {
        "T":   [13, 21, 33, 52, 84, 130, 210, 330, 520, 840, 1300],
        "Z":   [2, 3, 5, 9, 9, 19, 19, 36, 36, 72, 72],
        "H/2": [1.25, 2, 2, 2, 2, 4.5, 4.5, 10.5, 10.5, 10.5, 10.5]
    },
    (30, 50): {
        "T":   [16, 25, 39, 62, 100, 160, 250, 390, 620, 1000, 1600],
        "Z":   [2.5, 3.5, 6, 11, 11, 22, 22, 42, 42, 80, 80],
        "H/2": [1.25, 2, 2, 2, 2, 5.5, 5.5, 12.5, 12.5, 12.5, 12.5]
    },
    (50, 80): {
        "T":   [19, 30, 46, 74, 120, 190, 300, 460, 740, 1200, 1900],
        "Z":   [2.5, 4, 7, 13, 13, 25, 25, 48, 48, 90, 90],
        "H/2": [1.5, 2.5, 2.5, 2.5, 2.5, 6.5, 6.5, 15, 15, 15, 15]
    }
}

# ==============================
# Core Helper Functions
# ==============================
def find_nominal_range(nominal_size: float) -> Tuple[Optional[Tuple[float, float]], Optional[Dict[str, list]]]:
    """Finds the matching nominal range in the ISO table."""
    for (low, high), values in ISO_TABLE.items():
        if low <= nominal_size <= high:
            return (low, high), values
    return None, None


def calculate_iso_params(nominal_size: float, total_tolerance_mm: float):
    """
    Finds the ISO column for the given nominal midpoint and total tolerance (mm).
    Returns: (nominal_range, column_label, Z_mm, H_half_mm)
    """
    nominal_range, data = find_nominal_range(nominal_size)
    if data is None:
        return None, None, None, None

    T_values = data["T"]
    Z_values = data["Z"]
    H2_values = data["H/2"]

    total_tol_um = total_tolerance_mm * 1000  # mm -> µm

    selected_index = next((i for i, t_val in enumerate(T_values) if total_tol_um <= t_val), len(T_values) - 1)
    Z_val_mm = Z_values[selected_index] / 1000
    H_half_mm = H2_values[selected_index] / 1000

    return nominal_range, selected_index + 6, Z_val_mm, H_half_mm


# ==============================
# Main Function (Supports All Cases)
# ==============================
def calculate_go_no_go_extended(
    tol_type: str,
    nominal: Optional[float] = None,
    val1: Optional[float] = None,
    val2: Optional[float] = None,
    lower: Optional[float] = None,
    upper: Optional[float] = None
):
    """
    tol_type → "±", "+", "-", "++", "--", "/"
    """

    # Determine lower/upper based on tolerance type
    if tol_type == "±":
        lower_limit = nominal - val1
        upper_limit = nominal + val1

    elif tol_type == "--":
        lower_limit = nominal - val2
        upper_limit = nominal - val1

    elif tol_type == "++":
        lower_limit = nominal + val1
        upper_limit = nominal + val2

    elif tol_type == "-":
        lower_limit = nominal - val1
        upper_limit = nominal

    elif tol_type == "+":
        lower_limit = nominal
        upper_limit = nominal + val1

    elif tol_type == "/":
        lower_limit, upper_limit = lower, upper

    else:
        return {"error": "Invalid tolerance type."}

    total_tolerance = upper_limit - lower_limit
    nominal_mid = (upper_limit + lower_limit) / 2

    nominal_range, column, Z_val, H_half = calculate_iso_params(nominal_mid, total_tolerance)
    if nominal_range is None:
        return {"error": f"Nominal size {nominal_mid} mm is outside defined ISO table ranges."}

    go = round(upper_limit - Z_val, 5)
    no_go = round(lower_limit, 5)

    return {
        "go": go,
        "no_go": no_go,
        "h_half": H_half,
        "range": nominal_range,
        "column": column,
        "lower": lower_limit,
        "upper": upper_limit,
        "type": tol_type
    }


# ==============================
# CLI Test
# ==============================
if __name__ == "__main__":
    print("===== Gauge GO / NO-GO Calculator (ISO Extended) =====")
    tol_type = input("Enter type (±, +, -, ++, --, /): ").strip()

    if tol_type == "±":
        n = float(input("Nominal size (mm): "))
        t = float(input("Tolerance (mm): "))
        print(calculate_go_no_go_extended(tol_type, nominal=n, val1=t))

    elif tol_type in ["++", "--"]:
        n = float(input("Nominal size (mm): "))
        v1 = float(input("First tolerance (mm): "))
        v2 = float(input("Second tolerance (mm): "))
        print(calculate_go_no_go_extended(tol_type, nominal=n, val1=v1, val2=v2))

    elif tol_type in ["+", "-"]:
        n = float(input("Nominal size (mm): "))
        v1 = float(input("Tolerance (mm): "))
        print(calculate_go_no_go_extended(tol_type, nominal=n, val1=v1))

    elif tol_type == "/":
        lower = float(input("Lower limit (mm): "))
        upper = float(input("Upper limit (mm): "))
        print(calculate_go_no_go_extended(tol_type, lower=lower, upper=upper))

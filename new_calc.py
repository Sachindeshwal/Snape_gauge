# new_calc.py (Corrected IS:3455 –1971 / ISO Based GO–NO GO Logic)
"""
Supports two gauge modes:
 - gauge_type="snap"  -> for plain snap gauges (shaft basis)
     GO = ES - Z
     NO_GO = EI
 - gauge_type="plug"  -> for plain plug gauges (hole basis)
     GO = EI + Z
     NO_GO = ES - Z

Gauge Tolerance = ± (H/2)

EI = lower work limit
ES = upper work limit
"""

from typing import Dict, Tuple, Optional

# ==============================
# ISO Table Data (microns) — Snape table
# ==============================
ISO_TABLE: Dict[Tuple[float, float], Dict[str, list]] = {
    (0, 3): {
        "T":   [4, 6, 10, 14, 25, 40, 60, 100, 140, 250, 400, 600],
        "Z":   [1, 1.5, 1.5, 2, 5, 5, 10, 10, 20, 20, 40, 40],
        "H/2": [0.6, 1, 1, 1.5, 1.5, 1.5, 2, 2, 5, 5, 5, 5]
    },
    (3, 6): {
        "T":   [5, 8, 12, 18, 30, 48, 75, 120, 180, 300, 480, 750],
        "Z":   [1, 2, 2, 3, 6, 6, 12, 12, 24, 24, 48, 48],
        "H/2": [0.75, 1.25, 1.25, 2, 2, 2, 2.5, 2.5, 6, 6, 6, 6]
    },
    (6, 10): {
        "T":   [6, 9, 15, 22, 36, 58, 90, 150, 220, 360, 580, 900],
        "Z":   [1, 2, 2, 3, 7, 7, 14, 14, 28, 28, 56, 56],
        "H/2": [0.75, 1.25, 1.25, 2, 2, 2, 3, 3, 7.5, 7.5, 7.5, 7.5]
    },
    (10, 18): {
        "T":   [8, 11, 18, 27, 43, 70, 110, 180, 270, 430, 700, 1100],
        "Z":   [1.5, 2.5, 2.5, 4, 8, 8, 16, 16, 32, 32, 64, 64],
        "H/2": [1, 1.5, 1.5, 2.5, 2.5, 2.5, 4, 4, 9, 9, 9, 9]
    },
    (18, 30): {
        "T":   [9, 13, 21, 33, 52, 84, 130, 210, 330, 520, 840, 1300],
        "Z":   [1.5, 3, 3, 5, 9, 9, 19, 19, 36, 36, 72, 72],
        "H/2": [1.25, 2, 2, 3, 3, 3, 4.5, 4.5, 10.5, 10.5, 10.5, 10.5]
    },
    (30, 50): {
        "T":   [11, 16, 25, 39, 62, 100, 160, 250, 390, 620, 1000, 1600],
        "Z":   [2, 3.5, 3.5, 6, 11, 11, 22, 22, 42, 42, 80, 80],
        "H/2": [1.25, 2, 2, 3.5, 3.5, 3.5, 5.5, 5.5, 12.5, 12.5, 12.5, 12.5]
    },
    (50, 80): {
        "T":   [13, 19, 30, 46, 74, 120, 190, 300, 460, 740, 1200, 1900],
        "Z":   [2, 4, 4, 7, 13, 13, 25, 25, 48, 48, 90, 90],
        "H/2": [1.5, 2.5, 2.5, 4, 4, 4, 6.5, 6.5, 15, 15, 15, 15]
    }
}

# ==============================
# Helpers
# ==============================
def find_nominal_range(n: float):
    for (low, high), v in ISO_TABLE.items():
        if low <= n <= high:
            return (low, high), v
    return None, None

def get_iso_params(nominal_mid: float, tol: float):
    nominal_range, data = find_nominal_range(nominal_mid)
    if data is None:
        return None, None, None, None

    total_um = tol * 1000.0
    idx = next((i for i, t in enumerate(data["T"]) if total_um <= (t + 1e-9)), len(data["T"]) - 1)

    column_label = idx + 6
    Z_mm = data["Z"][idx] / 1000.0
    H_half_mm = data["H/2"][idx] / 1000.0

    return nominal_range, column_label, Z_mm, H_half_mm

# ==============================
# Main Calculation
# ==============================
def calculate_go_no_go_extended(tol_type: str,
                                nominal: Optional[float] = None,
                                val1: Optional[float] = None,
                                val2: Optional[float] = None,
                                lower: Optional[float] = None,
                                upper: Optional[float] = None,
                                gauge_type: str = "snap"):

    # Convert tolerance formats → EI/ES
    if tol_type == "±":
        EI = nominal - val1
        ES = nominal + val1
    elif tol_type == "-":
        EI = nominal - val1
        ES = nominal
    elif tol_type == "+":
        EI = nominal
        ES = nominal + val1
    elif tol_type == "--":
        EI = nominal - val2
        ES = nominal - val1
    elif tol_type == "++":
        EI = nominal + val1
        ES = nominal + val2
    elif tol_type == "/":
        # ✅ FIX — ensure min → EI & max → ES (Snape input is Max/Min order)
        EI, ES = min(lower, upper), max(lower, upper)
    else:
        return {"error": "Invalid tolerance type"}

    tol = ES - EI
    nominal_mid = (EI + ES) / 2.0

    rng, col, Z, H2 = get_iso_params(nominal_mid, tol)
    if rng is None:
        return {"error": f"Nominal {nominal_mid} mm outside ISO ranges"}

    gauge_type = gauge_type.lower()

    if gauge_type == "snap":
        GO = round(ES - Z, 5)
        NO_GO = round(EI, 5)
    elif gauge_type == "plug":
        GO = round(EI + Z, 5)
        NO_GO = round(ES - Z, 5)
    else:
        return {"error": "Invalid gauge_type; use 'snap' or 'plug'"}

    return {
        "go": GO, 
        "no_go": NO_GO,
        "gauge_tol": H2,
        "range": rng,
        "column": col,
        "EI": round(EI, 5),
        "ES": round(ES, 5),
        "Z": Z
    }

if __name__ == "__main__":
    print(calculate_go_no_go_extended("±", nominal=31.75, val1=0.05, gauge_type="snap"))

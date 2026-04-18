#!/usr/bin/env python3


"""
Trajectory Curve Matcher via Root Mean Square Error Between Two Vectors

The original use-case is analysis and matching using the vendor-provided calibration
data for the Hi-Lux Leatherwood Auto-Ranging Telescope (ART) M1000-PRO.
See: https://hi-luxoptics.com/collections/automatic-ranging-trajectory-art/products/m1000-pro

Basic Features:

- Accepts trajectory curves as a dictionary
- Computes best match using normalized RMSE
- Outputs best setting, curve, and similarity score
- Curve tables store as JSON files (with basic validation)

Design Notes:

- Similarity metric uses normalized RMSE, which is:
  - Scale-aware
  - Robust to magnitude differences
  - Interpretable as a percentage

- Validation:
  - Enforces equal-length curves
  - Defensive parsing with clear exceptions

- Extensibility:
  - Swap similarity metric easily
  - Add interpolation if user curve has different distances
  - Can be upgraded to NumPy for large datasets

- Performance:
  - Efficient for this (very small) dataset size
  - O(n * m) where:
    - n = number of table rows
    - m = points per curve

Compatibility: Python 3.11+

Linter: ruff check trajectory-curve-match.py --extend-select F,B,UP
"""


from __future__ import annotations
from dataclasses import dataclass
import math
import sys
import json


# ---------------------------
# Data Models
# ---------------------------

@dataclass(frozen=True)
class TrajectoryCurve:
    """Represents a trajectory curve for a given setting."""
    setting: int
    values: list[float]


@dataclass(frozen=True)
class MatchResult:
    """Represents the result of a curve match."""
    setting: int
    curve: list[float]
    similarity: float  # percentage (0–100)


# ---------------------------
# Similarity Calculation
# ---------------------------

def _rmse(a: list[float], b: list[float]) -> float:
    """Compute Root Mean Square Error between two vectors."""
    if len(a) != len(b):
        raise ValueError("Curve lengths must match.")

    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)) / len(a))


def _normalize_rmse(rmse: float, reference: list[float]) -> float:
    """Normalize RMSE based on value range."""
    value_range = max(reference) - min(reference)

    return rmse / value_range if value_range else 0.0


def similarity_score(a: list[float], b: list[float]) -> float:
    """
    Compute similarity score (0–100).

    similarity = (1 - normalized_rmse) * 100
    """
    rmse_val = _rmse(a, b)
    norm = _normalize_rmse(rmse_val, a)

    return max(0.0, (1.0 - norm) * 100.0)


# ---------------------------
# Core Logic
# ---------------------------

def build_curves(curve_table: dict[int, list[float]]) -> dict[int, TrajectoryCurve]:
    """
    Convert raw dictionary into TrajectoryCurve objects.

    Args:
        curve_table: Mapping of setting -> curve values

    Returns:
        Structured curve dictionary
    """
    if not curve_table:
        raise ValueError("Input table is empty.")

    return {
        setting: TrajectoryCurve(setting=setting, values=values)

        for setting, values in curve_table.items()
    }


def find_best_match(
    user_curve: list[float],
    curves: dict[int, TrajectoryCurve],
) -> MatchResult:
    """Find best matching trajectory curve."""
    best_setting: int | None = None
    best_score: float = -1.0
    best_curve: list[float] | None = None

    for setting, curve in curves.items():
        if len(curve.values) != len(user_curve):
            raise ValueError(
                f"Length mismatch for setting {setting}: "
                f"{len(curve.values)} != {len(user_curve)}"
            )

        score = similarity_score(user_curve, curve.values)

        if score > best_score:
            best_setting = setting
            best_score = score
            best_curve = curve.values

    if best_setting is None or best_curve is None:
        raise RuntimeError("Failed to determine best match.")

    return MatchResult(
        setting=best_setting,
        curve=best_curve,
        similarity=round(best_score, 2),
    )


def validate_table(table: dict[int, list[float]]) -> None:
    lengths = {len(v) for v in table.values()}

    if len(lengths) != 1:
        raise ValueError(f"Inconsistent curve lengths: {lengths}")


def load_trajectory_table(path: str) -> dict[int, list[float]]:
    """
    Load trajectory table from JSON file.

    Args:
        path: Path to JSON file

    Returns:
        Dictionary mapping setting -> curve
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    try:
        return {int(k): list(map(float, v)) for k, v in data.items()}
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid trajectory table format.") from exc


# ---------------------------
# Example Usage
# ---------------------------

def main() -> None:
    """Example execution using dictionary input."""

    # User-supplied data table. Source: AB Quantum v3.7.1
    # Values for 7.62 NATO M80 as exemplar ballistics:
    # G1 BC = 0.393, MV=2750 fps. Curve data is in MOA.

    user_curve = [0.0, -2.6, -5.9, -9.8, -14.4, -19.9, -26.3, -33.8, -42.4]

    try:
        # two options: "basic-curve-table.json" or "extended-curve-table.json"
        curve_table = load_trajectory_table("extended-curve-table.json")

        validate_table(curve_table)
        curves = build_curves(curve_table)
        result = find_best_match(user_curve, curves)

        print()
        print("Best Match Result")
        print("-----------------")
        print(f"Setting:   {result.setting}")
        print(f"Curve:     {result.curve}")
        print(f"User Data: {user_curve}")
        print(f"Match:     {result.similarity:.2f}%")
        print()

    except (ValueError, RuntimeError) as exc:
        print(exc, file=sys.stderr)

        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()

# end of script

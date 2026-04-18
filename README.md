# Trajectory Curve Matcher

A tool for matching a user-provided trajectory curve against a predefined dataset using a normalized RMSE similarity metric.

---

## Overview

This project performs comparative analysis between a pre-calculated ballistic trajectory curve table and user-supplied trajectory curve data in order to determines the closest matching setting.

The original use-case is analysis and matching using the vendor-provided calibration data for the Hi-Lux Leatherwood Auto-Ranging Telescope (ART) M1000-PRO. See: https://hi-luxoptics.com/collections/automatic-ranging-trajectory-art/products/m1000-pro

Given a user-provided curve (e.g., drop values across distances), the tool:

* Compares it against a library of known curves
* Computes similarity using normalized Root Mean Square Error (RMSE)
* Returns:

  * Best matching setting
  * Associated reference curve
  * Similarity score (%)

---

## Features

* Deterministic and reproducible matching
* Scale-aware similarity metric (normalized RMSE)
* Type-safe, modular Python code (PEP 8 / PEP 20 compliant)
* Defensive validation for input consistency
* Easy to extend (CLI, API, NumPy acceleration)


---

## Requirements

* Python 3.11+
* No external dependencies (standard library only)

---

## How It Works

### Input

* User Curve: A list of float values representing trajectory drop at fixed distances
* Reference Table: Dictionary mapping:

```
setting (int) -> List[float] (trajectory values)
```

### Algorithm

1. Validate curve lengths
2. Compute RMSE between user curve and each reference curve
3. Normalize RMSE using the curve’s value range
4. Convert to similarity score:

```
similarity = (1 - normalized_rmse) * 100
```

5. Select the highest scoring match

---

## Usage

### Example

At present, users must edit the script to input their curve data, but running this script is very simple:

```
python3 /trajectory-curve-match.py
```

Output

```
Best Match Result
-----------------
Setting:   315
Curve:     [0.0, -4.0, -8.6, -12.8, -16.0, -20.2, -26.5, -33.9, -41.8]
User Data: [0.0, -2.6, -5.9, -9.8, -14.4, -19.9, -26.3, -33.8, -42.4]
Match:     96.37%
```

---

## Validation

The system enforces some consistency rules:

* Equal-length curves across dataset
* Equal-length user input vs reference curves

Optional validation helper:

```python
def validate_table(curve_table):
    lengths = {len(v) for v in curve_table.values()}

    if len(lengths) != 1:
        raise ValueError(f"Inconsistent curve lengths: {lengths}")
```

---

## Design Decisions

### Why Normalized RMSE?

* Handles magnitude differences across curves
* Provides intuitive percentage-based similarity
* Penalizes large deviations more than small ones

### Why No External Dependencies?

* Keeps deployment simple
* Ensures portability (embedded / constrained environments)

---

## Performance

* Time Complexity: O(n × m)

  * n = number of curves
  * m = points per curve
* Efficient for typical datasets (<10,000 curves)

---

## Possible Future Enhancements

* Distance-weighted similarity (e.g., prioritize long-range accuracy)
* Migrating curve table data to a config file
* CLI interface (`argparse`) for user-supplied curve data
* Format unit testing harness

---

## Contributing

Contributions are welcome. Please observe the following coding style requirements:

1. Follow PEP 8 / PEP 20
2. Include type hints
3. Add tests/validation for new functionality (assuming a test framework is established)
4. Keep functions small and composable

---

## Disclaimer

This tool performs mathematical curve matching only. It does not account for real-world ballistic variables such as:

* Wind
* Temperature
* Humidity
* Altitude
* Spin drift
* Coriolis effect(s)
* Projectile characteristics

---

# License

This tool is released under the Apache 2.0 license. See the LICENSE file in this repo for details.

# Built With

* [Python](https://www.python.org) designed by Guido van Rossum

## Author

Rick Pelletier

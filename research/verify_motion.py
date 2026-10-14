"""Verify the archived motion data without rerunning optimization.

Uses Python's standard library only. The supplied paired trajectories are
already phase-aligned; this script does not fit, shift, or realign them.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        content = (ROOT / item["path"]).read_bytes()
        if hashlib.sha256(content).hexdigest() != item["sha256"]:
            raise ValueError(f"Archive integrity check failed: {item['path']}")

    reference = rows(ROOT / "motion-reference.csv")
    paired = rows(ROOT / "strict-phase-trajectories.csv")
    metadata = json.loads((ROOT / "motion-reference-metadata.json").read_text(encoding="utf-8"))
    count = int(metadata["sample_count"])
    if len(reference) != count or len(paired) != count or count != 76:
        raise ValueError("Expected 76 synchronized reference and comparison states.")

    residual_squares: dict[str, list[float]] = {"tip": [], "wrist": []}
    maximum_target_difference = 0.0
    coordinate_rmse: dict[str, float] = {}
    for index, (target, comparison) in enumerate(zip(reference, paired)):
        if int(target["phase_index"]) != index or int(comparison["phase_index"]) != index:
            raise ValueError("Phase indices must remain in their published order.")
        if not math.isclose(float(target["phase_equal_arc"]), index / count, abs_tol=1e-12):
            raise ValueError("Reference phase does not match the equal-arc grid.")
        for point in ("tip", "wrist"):
            squared_distance = 0.0
            for axis in "xyz":
                reference_value = float(target[f"{point}_{axis}_mm"])
                target_value = float(comparison[f"target_{point}_{axis}"])
                generated_value = float(comparison[f"generated_{point}_{axis}"])
                if not all(math.isfinite(v) for v in (reference_value, target_value, generated_value)):
                    raise ValueError("Non-finite coordinate found in the archive.")
                difference = abs(reference_value - target_value)
                maximum_target_difference = max(maximum_target_difference, difference)
                if difference > 1e-8:
                    raise ValueError("Comparison target differs from the published reference.")
                squared_distance += (generated_value - target_value) ** 2
            residual_squares[point].append(squared_distance)

    for point in ("tip", "wrist"):
        for axis in "xyz":
            coordinate_rmse[f"{point}_{axis}"] = math.sqrt(math.fsum(
                (float(row[f"generated_{point}_{axis}"]) - float(row[f"target_{point}_{axis}"])) ** 2
                for row in paired
            ) / count)

    point_rmse = {
        point: math.sqrt(math.fsum(values) / count)
        for point, values in residual_squares.items()
    }
    combined = math.sqrt(math.fsum(
        residual_squares["tip"] + residual_squares["wrist"]
    ) / (2 * count))
    print(json.dumps({
        "check": "published paired-trajectory data verification",
        "archive_hashes_verified": len(manifest["files"]),
        "sample_count": count,
        "units": "mm",
        "phase": "coupled six-dimensional equal-arc coordinate, not elapsed time",
        "maximum_reference_difference_mm": maximum_target_difference,
        "point_position_rmse_mm": point_rmse,
        "combined_point_position_rmse_mm": combined,
        "coordinate_rmse_mm": coordinate_rmse,
        "limits": "No mechanism solve, optimization rerun, or aerodynamic validation performed."
    }, indent=2))


if __name__ == "__main__":
    main()

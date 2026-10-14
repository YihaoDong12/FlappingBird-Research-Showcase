# Motion data and mechanism source

This is a compact, public subset of the project's existing motion and mechanism archive. It supports inspection of the motion reference and verification of the stored paired-trajectory errors. It is not a complete raw-data release or a standalone reproduction of the entire research pipeline.

## Verify the supplied data

Python 3.10 or later is sufficient; the verification script has no third-party dependencies. From the website repository directory:

```sh
python research/verify_motion.py
```

The script checks the SHA-256 hashes of all seven inherited files, verifies 76 synchronized states, checks that the comparison target matches the reference, and calculates same-index 3D position errors. It does not realign the curves or rerun a solver. The combined error is the root mean square of the two points' Euclidean distances, not an average over six individual coordinates.

## Contents

| File | What it contains |
| --- | --- |
| `motion-reference.csv` | Processed wrist and wingtip reference coordinates, in millimetres. |
| `motion-reference-metadata.json` | Initialization, coordinate and coupled-resampling metadata from the source archive. |
| `strict-phase-trajectories.csv` | Stored target and generated coordinates in the same reference frame. |
| `model/fourbar3d_python.py` | Original analytical 3D mechanism model. |
| `model/fourbar_optimization.py` | Original optimization and feasibility-checking implementation. |
| `parameters/optimization-input.json` | Frozen optimization input contract. It is not itself an optimization result. |
| `parameters/final-variables-and-bounds.csv` | Selected stored-event variables and bounds. |
| `source-manifest.json` | Source revision, original relative paths and hashes. |

The CSV phase is a shared, closed **six-dimensional wrist-plus-wingtip arc-length coordinate** on `[0,1)`, not elapsed time or a measured flapping frequency. The two landmarks remain paired. These are initialized and resampled motion targets, not raw camera detections.

## Scope and provenance

The seven inherited files are byte-identical to committed public files at source revision `a6c2c00e56c442ddad382ef75d5a2eb66678076b`, under `public/reproducibility/`. Filenames have been shortened only at the destination; the original metadata's source filenames are preserved. No unpublished recordings, manuscript source, local work-in-progress folders or untracked results are included.

The original archive identifies the selected event as evaluation 1,074,004 of a 12-hour cold-start run. It explicitly does not claim a finalized terminal checkpoint or a universal global optimum. This subset preserves that limitation.

The model sources use NumPy and SciPy and retain their original scientific comments and interfaces. Their standalone entry points also expect legacy MATLAB inputs and/or checkpoints that are **not included here**. Therefore, running those entry points directly is not the documented verification route. The script above verifies the published data; it does not independently recreate the mechanism trajectories. Complete raw-data access and an end-to-end solver package remain separate deliverables.

## Aerodynamic work

The website's fluid–structure-coupled PINN section describes method development and planned experimental validation. This data package contains no trained PINN weights, calibrated wind-tunnel force dataset, measured vortex field, or validated aerodynamic prediction results. Generated research-significance illustrations are concepts, not experimental evidence.

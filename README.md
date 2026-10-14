# Flapping Bird Research

An independent, English-language, media-led research showcase: demonstrated flight, ongoing motion and mechanism research, and future experimental work. This repository is separate from the earlier project showcase; publishing it does not replace that website.

## Preview locally

Install Node.js, open a terminal in this directory and run:

```sh
node server.cjs --port 3013
```

Open `http://localhost:3013/`. Choose another available port by changing `3013`. The site is static and uses relative asset paths, so it can also be served by another static web server or from a GitHub Pages repository subpath.

## Publish with GitHub Pages

The included GitHub Actions workflow builds and deploys the site when changes are pushed to `main`. In the repository's **Settings → Pages**, select **GitHub Actions** as the build source.

To create the deployment package locally:

```sh
node scripts/build-site.cjs
```

The output is `_site/`. The build intentionally refuses to overwrite an existing output directory; keep or relocate an earlier build before creating another. Only public website assets and the explicitly included research package belong in a deployment. Local preview files and `.source-materials/` are not published.

## Research resources

The [`research/`](research/README.md) folder contains a compact, already-published motion reference, archived mechanism source and parameters, plus a dependency-free data-verification script. It is not presented as a full raw-data archive or a complete optimizer reproduction.

```sh
python research/verify_motion.py
```

## Evidence and illustrations

- Flight and marker-tracking videos show existing footage. Mechanism videos show simulations.
- Wind-tunnel aerodynamic analysis and the fluid–structure-coupled PINN are ongoing method and experiment-design work. The manuscript draft does not yet establish validated force-prediction accuracy or completed wake measurements.
- Future-work and research-significance illustrations are conceptual, not photographs of completed experiments or computed flow results. Image provenance is recorded in `design/`.
- The aerodynamic section uses concise, code-drawn animated schematics of the planned experiment and the manuscript's modelling workflow. Motion and airflow traces are illustrative; the unpublished manuscript and its full source archive are not distributed here.

Use concise English labels, preserve the three-section visual hierarchy and keep scientific claims aligned with the evidence available. Do not activate visitor tracking or publish private research material as part of routine site updates.

# Simi Search

[![Test and lint](https://github.com/ThinhUMP/simi_search/actions/workflows/test-and-lint.yml/badge.svg)](https://github.com/ThinhUMP/simi_search/actions/workflows/test-and-lint.yml)
[![Documentation Status](https://readthedocs.org/projects/simi-search/badge/?version=latest)](https://simi-search.readthedocs.io/en/latest/?badge=latest)

Ligand similarity search benchmarking on LIT-PCBA.

Simi Search prepares LIT-PCBA targets, ranks validation molecules by similarity
to active training ligands, and reports virtual-screening metrics focused on
early enrichment. The project intentionally avoids docking, structure scores,
RF/CNN scoring functions, interaction fingerprints, and consensus scoring so
that ligand similarity can be evaluated directly.

## Features

- Official LIT-PCBA archive download and normalization.
- Similarity-only benchmark protocol for train-active to validation-library retrieval.
- Dependency-free hashed SMILES fingerprint baseline.
- Optional RDKit Morgan/ECFP fingerprint backend.
- Early-recognition metrics: `EF1%`, `EF5%`, `BEDROC20`, `ROC_AUC`, and `PR_AUC`.
- Sphinx/RST documentation and release workflows for PyPI, conda, Docker, and Read the Docs.

## Installation

Simi Search targets Python 3.11.

Install the base package:

```bash
pip install simi-search
```

Install with RDKit support:

```bash
pip install "simi-search[rdkit]"
```

In conda environments, RDKit is often easiest to install from conda-forge:

```bash
conda install -c conda-forge rdkit
pip install simi-search
```

## Quick Start

Download and prepare the AVE-unbiased LIT-PCBA benchmark:

```bash
download-lit-pcba --data-dir data --variant ave
```

Run all processed targets with the lightweight hashed SMILES backend:

```bash
benchmark-similarity \
  --data-dir data/processed/lit_pcba_ave \
  --fingerprint hashed \
  --output results/lit_pcba_similarity_metrics.csv
```

Run with RDKit Morgan fingerprints:

```bash
benchmark-similarity \
  --data-dir data/processed/lit_pcba_ave \
  --fingerprint rdkit \
  --output results/lit_pcba_rdkit_metrics.csv
```

Run a single target:

```bash
benchmark-similarity \
  --data-dir data/processed/lit_pcba_ave \
  --target PPARG \
  --fingerprint rdkit \
  --output results/PPARG_rdkit_metrics.csv
```

## Output

The benchmark writes one CSV row per target with:

- `Target`
- `Method`
- `Train_Queries`
- `Compounds`
- `Actives`
- `EF1%`
- `EF5%`
- `BEDROC20`
- `ROC_AUC`
- `PR_AUC`
- `Top1%_Actives`
- `Top5%_Actives`

## Docker

The release workflow publishes:

```text
ghcr.io/thinhump/simi_search
```

Example:

```bash
docker run --rm \
  -v "$PWD/data:/app/data" \
  -v "$PWD/results:/app/results" \
  ghcr.io/thinhump/simi_search:latest \
  --data-dir data/processed/lit_pcba_ave \
  --output results/lit_pcba_similarity_metrics.csv
```

## Documentation

Sphinx documentation lives in `docs/` and is configured for Read the Docs via
`.readthedocs.yaml`.

Build locally:

```bash
python -m pip install -r requirements.txt
sphinx-build -W -b html docs docs/_build/html
```

## Development

```bash
python -m pip install -r requirements.txt
ruff check .
ruff format --check .
python -m unittest discover -s tests
python -m build
sphinx-build -W -b html docs docs/_build/html
```

## Release

- PyPI: GitHub release triggers `.github/workflows/release-pypi.yml`.
- Conda: GitHub release triggers `.github/workflows/release-conda.yml`; requires `ANACONDA_API_TOKEN`.
- Docker: GitHub release or `v*` tag triggers `.github/workflows/release-docker.yml`.
- Read the Docs: configured by `.readthedocs.yaml`.

## License

Apache-2.0. See `LICENSE`.

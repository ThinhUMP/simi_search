# Changelog

All notable changes to `simi-search` are documented here.

## 0.1.0 - 2026-05-10

### Added

- LIT-PCBA AVE-unbiased downloader and CSV normalizer.
- Similarity-search benchmark using active training ligands as query/reference molecules.
- Dependency-free hashed SMILES n-gram fingerprints.
- Optional RDKit Morgan/ECFP fingerprint backend via `simi-search[rdkit]`.
- CLI commands:
  - `download-lit-pcba`
  - `benchmark-similarity`
- Ranking metrics: `EF1%`, `EF5%`, `BEDROC20`, `ROC_AUC`, `PR_AUC`, top-1% active count, and top-5% active count.
- OOP modules for fingerprints, similarity search, benchmark orchestration, metrics, and domain models.
- Sphinx/RST documentation with scientific styling.
- Packaging and release infrastructure for PyPI, conda, Docker, GitHub Actions, Dependabot, and Read the Docs.
- Apache-2.0 package metadata aligned with the repository license.

### Changed

- Renamed the Python import package to `simi_search`.
- Set project metadata and release URLs for `https://github.com/ThinhUMP/simi_search`.
- Updated Docker release image to `ghcr.io/thinhump/simi_search`.

### Removed

- Docking, RF, CNN, IFP, and consensus-score benchmarking from the project scope.
- Internal planning files in favor of this changelog and public documentation.

"""Run ligand similarity benchmarking on processed LIT-PCBA data."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from simi_search.benchmark import LitPcbaTargetRepository, SimilarityBenchmarkRunner
from simi_search.fingerprints import build_fingerprinter
from simi_search.search import MaxActiveSimilaritySearch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/processed/lit_pcba_ave"),
        help="Processed LIT-PCBA directory created by download_lit_pcba.",
    )
    parser.add_argument("--target", action="append", help="Target to benchmark. Repeat for multiple targets.")
    parser.add_argument("--output", type=Path, default=Path("results/lit_pcba_similarity_metrics.csv"))
    parser.add_argument(
        "--fingerprint",
        choices=["hashed", "rdkit"],
        default="hashed",
        help="Fingerprint backend. Use 'rdkit' for Morgan/ECFP fingerprints when RDKit is installed.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repository = LitPcbaTargetRepository(args.data_dir)
    try:
        fingerprinter = build_fingerprinter(args.fingerprint)
    except (ImportError, ValueError) as error:
        raise SystemExit(str(error)) from error
    runner = SimilarityBenchmarkRunner(
        repository=repository,
        searcher=MaxActiveSimilaritySearch(fingerprinter=fingerprinter, method_name=f"{args.fingerprint}_tanimoto"),
    )
    try:
        results = runner.run(args.target)
    except (ImportError, ValueError) as error:
        raise SystemExit(str(error)) from error

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for result in results:
        metrics = result.metrics
        rows.append(
            {
                "Target": result.target,
                "Method": f"{result.method}_max_train_active",
                "Train_Queries": result.train_queries,
                "Compounds": metrics.compounds,
                "Actives": metrics.actives,
                "EF1%": f"{metrics.ef1:.6g}",
                "EF5%": f"{metrics.ef5:.6g}",
                "BEDROC20": f"{metrics.bedroc20:.6g}",
                "ROC_AUC": f"{metrics.roc_auc:.6g}",
                "PR_AUC": f"{metrics.pr_auc:.6g}",
                "Top1%_Actives": metrics.top1_actives,
                "Top5%_Actives": metrics.top5_actives,
            }
        )

    fieldnames = list(rows[0])
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote simi-search metrics to {args.output}")
    for row in rows:
        print(
            f"{row['Target']:10s} queries={row['Train_Queries']} "
            f"EF1%={row['EF1%']} BEDROC20={row['BEDROC20']} ROC_AUC={row['ROC_AUC']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI for preparing LIT-PCBA as benchmark CSV files."""

from __future__ import annotations

import argparse
from pathlib import Path

from simi_search.datasets.lit_pcba import ARCHIVES, prepare_lit_pcba


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory for archives, raw extraction, and processed CSVs.",
    )
    parser.add_argument(
        "--variant",
        choices=sorted(ARCHIVES),
        default="ave",
        help="LIT-PCBA archive variant to download.",
    )
    parser.add_argument("--url", help="Override the source archive URL.")
    parser.add_argument("--archive-path", type=Path, help="Use this archive path instead of the default.")
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Extract and process an existing archive without downloading.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    benchmark_dir, summaries = prepare_lit_pcba(
        data_dir=args.data_dir,
        variant=args.variant,
        url=args.url,
        archive_path=args.archive_path,
        skip_download=args.skip_download,
    )

    print(f"Wrote normalized LIT-PCBA benchmark CSVs to {benchmark_dir}")
    for summary in summaries:
        print(
            f"{summary.target:12s} {summary.split:10s} "
            f"n={summary.compounds} actives={summary.actives} inactives={summary.inactives}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Download and normalize the LIT-PCBA benchmark dataset.

The official LIT-PCBA distribution provides one directory per target with
SMILES files named active/inactive plus training/validation variants. This
module downloads the archive, extracts it defensively, and writes simple CSV
files that benchmark scripts can consume without knowing the original layout.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import tarfile
import tempfile
import urllib.request
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

OFFICIAL_BASE_URL = "https://drugdesign.unistra.fr/LIT-PCBA/Files"
ARCHIVES = {
    "ave": f"{OFFICIAL_BASE_URL}/AVE_unbiased.tgz",
    "full": f"{OFFICIAL_BASE_URL}/full_data.tgz",
}

SPLIT_FILES = {
    "all": ("active.smi", "inactive.smi"),
    "train": ("active_T.smi", "inactive_T.smi"),
    "validation": ("active_V.smi", "inactive_V.smi"),
}


@dataclass(frozen=True)
class CompoundRecord:
    target: str
    split: str
    label: int
    class_name: str
    smiles: str
    compound_id: str


@dataclass(frozen=True)
class TargetSummary:
    target: str
    split: str
    compounds: int
    actives: int
    inactives: int


def download_archive(url: str, archive_path: Path, *, timeout: int = 60) -> Path:
    """Download ``url`` to ``archive_path`` unless it already exists."""

    archive_path = archive_path.expanduser().resolve()
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists() and archive_path.stat().st_size > 0:
        return archive_path

    request = urllib.request.Request(url, headers={"User-Agent": "simi-search/0.1"})
    with (
        urllib.request.urlopen(request, timeout=timeout) as response,
        tempfile.NamedTemporaryFile(delete=False, dir=str(archive_path.parent)) as tmp,
    ):
        tmp_path = Path(tmp.name)
        shutil.copyfileobj(response, tmp)

    tmp_path.replace(archive_path)
    return archive_path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def extract_archive(archive_path: Path, extract_dir: Path) -> Path:
    """Extract a tar archive while rejecting path traversal members."""

    archive_path = archive_path.expanduser().resolve()
    extract_dir = extract_dir.expanduser().resolve()
    extract_dir.mkdir(parents=True, exist_ok=True)

    with tarfile.open(archive_path, "r:*") as archive:
        for member in archive.getmembers():
            destination = (extract_dir / member.name).resolve()
            if os.path.commonpath([str(extract_dir), str(destination)]) != str(extract_dir):
                raise ValueError(f"Unsafe archive member path: {member.name}")
        archive.extractall(extract_dir, filter="data")
    return extract_dir


def find_target_dirs(root: Path) -> list[Path]:
    """Return directories containing LIT-PCBA active/inactive SMILES files."""

    root = root.expanduser().resolve()
    targets = set()
    for file_name_pair in SPLIT_FILES.values():
        for file_name in file_name_pair:
            for smi_path in root.rglob(file_name):
                targets.add(smi_path.parent)
    return sorted(targets, key=lambda path: path.name)


def iter_smi_records(path: Path, *, label: int, class_name: str) -> Iterator[tuple[str, str, int, str]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if len(parts) < 2:
                raise ValueError(f"{path}:{line_number} must contain SMILES and compound id")
            yield parts[0], parts[1], label, class_name


def iter_compounds(dataset_root: Path) -> Iterator[CompoundRecord]:
    for target_dir in find_target_dirs(dataset_root):
        target = target_dir.name
        for split, (active_name, inactive_name) in SPLIT_FILES.items():
            active_path = target_dir / active_name
            inactive_path = target_dir / inactive_name
            if active_path.exists():
                for smiles, compound_id, label, class_name in iter_smi_records(
                    active_path, label=1, class_name="Active"
                ):
                    yield CompoundRecord(target, split, label, class_name, smiles, compound_id)
            if inactive_path.exists():
                for smiles, compound_id, label, class_name in iter_smi_records(
                    inactive_path, label=0, class_name="Inactive"
                ):
                    yield CompoundRecord(target, split, label, class_name, smiles, compound_id)


def write_benchmark_csvs(dataset_root: Path, output_dir: Path) -> list[TargetSummary]:
    """Write one normalized CSV per target/split and return row-count summaries."""

    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    grouped: dict[tuple[str, str], list[CompoundRecord]] = {}
    for record in iter_compounds(dataset_root):
        grouped.setdefault((record.target, record.split), []).append(record)

    summaries: list[TargetSummary] = []
    fieldnames = ["ID", "SMILES", "Real_Class", "Label", "Target", "Split"]
    for (target, split), records in sorted(grouped.items()):
        target_output_dir = output_dir / target
        target_output_dir.mkdir(parents=True, exist_ok=True)
        output_path = target_output_dir / f"{target}-LIT-PCBA-{split}.csv"
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(
                    {
                        "ID": record.compound_id,
                        "SMILES": record.smiles,
                        "Real_Class": record.class_name,
                        "Label": record.label,
                        "Target": record.target,
                        "Split": record.split,
                    }
                )

        actives = sum(record.label for record in records)
        summaries.append(
            TargetSummary(
                target=target,
                split=split,
                compounds=len(records),
                actives=actives,
                inactives=len(records) - actives,
            )
        )
    return summaries


def write_manifest(
    *,
    archive_path: Path,
    dataset_root: Path,
    output_dir: Path,
    source_url: str,
    variant: str,
    summaries: Iterable[TargetSummary],
) -> Path:
    manifest = {
        "dataset": "LIT-PCBA",
        "variant": variant,
        "source_url": source_url,
        "archive": str(archive_path),
        "archive_sha256": sha256_file(archive_path),
        "extracted_root": str(dataset_root),
        "benchmark_csv_dir": str(output_dir),
        "targets": [summary.__dict__ for summary in summaries],
    }
    manifest_path = output_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return manifest_path


def prepare_lit_pcba(
    *,
    data_dir: Path,
    variant: str = "ave",
    url: str | None = None,
    archive_path: Path | None = None,
    skip_download: bool = False,
) -> tuple[Path, list[TargetSummary]]:
    """Download/extract LIT-PCBA and create normalized benchmark CSV files."""

    if variant not in ARCHIVES:
        raise ValueError(f"Unknown LIT-PCBA variant {variant!r}; choose one of {sorted(ARCHIVES)}")

    data_dir = data_dir.expanduser().resolve()
    source_url = url or ARCHIVES[variant]
    archive_path = (archive_path or data_dir / "archives" / Path(source_url).name).expanduser().resolve()
    extract_dir = data_dir / "raw" / f"lit_pcba_{variant}"
    benchmark_dir = data_dir / "processed" / f"lit_pcba_{variant}"

    if not skip_download:
        download_archive(source_url, archive_path)
    elif not archive_path.exists():
        raise FileNotFoundError(f"Archive not found with --skip-download: {archive_path}")

    extract_archive(archive_path, extract_dir)
    summaries = write_benchmark_csvs(extract_dir, benchmark_dir)
    if not summaries:
        raise ValueError(f"No LIT-PCBA target SMILES files found under {extract_dir}")

    write_manifest(
        archive_path=archive_path,
        dataset_root=extract_dir,
        output_dir=benchmark_dir,
        source_url=source_url,
        variant=variant,
        summaries=summaries,
    )
    return benchmark_dir, summaries

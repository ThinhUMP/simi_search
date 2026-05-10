"""Benchmark orchestration for simi-search LIT-PCBA experiments."""

from __future__ import annotations

import csv
from pathlib import Path

from simi_search.metrics import compute_ranking_metrics
from simi_search.models import Molecule, SimilarityResult
from simi_search.search import MaxActiveSimilaritySearch


class LitPcbaTargetRepository:
    """Read processed LIT-PCBA target CSVs."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir.expanduser().resolve()

    def discover_targets(self) -> list[str]:
        targets: list[str] = []
        for child in self.data_dir.iterdir():
            if not child.is_dir():
                continue
            if self.train_csv(child.name).exists() and self.validation_csv(child.name).exists():
                targets.append(child.name)
        return sorted(targets)

    def train_csv(self, target: str) -> Path:
        return self.data_dir / target / f"{target}-LIT-PCBA-train.csv"

    def validation_csv(self, target: str) -> Path:
        return self.data_dir / target / f"{target}-LIT-PCBA-validation.csv"

    def read_split(self, path: Path) -> list[Molecule]:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {"ID", "SMILES", "Label", "Target", "Split"}
            missing = required.difference(reader.fieldnames or [])
            if missing:
                raise ValueError(f"{path} is missing required columns: {sorted(missing)}")
            return [
                Molecule(
                    compound_id=row["ID"],
                    smiles=row["SMILES"],
                    label=int(row["Label"]),
                    target=row["Target"],
                    split=row["Split"],
                )
                for row in reader
            ]


class SimilarityBenchmarkRunner:
    """Run active-query similarity retrieval for one or more LIT-PCBA targets."""

    def __init__(
        self,
        *,
        repository: LitPcbaTargetRepository,
        searcher: MaxActiveSimilaritySearch | None = None,
    ) -> None:
        self.repository = repository
        self.searcher = searcher or MaxActiveSimilaritySearch()

    def run_target(self, target: str) -> SimilarityResult:
        train = self.repository.read_split(self.repository.train_csv(target))
        validation = self.repository.read_split(self.repository.validation_csv(target))
        active_queries = [molecule for molecule in train if molecule.label == 1]
        scores = self.searcher.score(active_queries, validation)
        labels = [molecule.label for molecule in validation]
        return SimilarityResult(
            target=target,
            method=self.searcher.method_name,
            train_queries=len(active_queries),
            metrics=compute_ranking_metrics(labels, scores),
        )

    def run(self, targets: list[str] | None = None) -> list[SimilarityResult]:
        selected_targets = sorted(targets) if targets else self.repository.discover_targets()
        if not selected_targets:
            raise ValueError(f"No processed LIT-PCBA targets found under {self.repository.data_dir}")
        return [self.run_target(target) for target in selected_targets]

"""Shared domain models for simi-search benchmarking."""

from __future__ import annotations

from dataclasses import dataclass

from simi_search.metrics import RankingMetrics


@dataclass(frozen=True)
class Molecule:
    compound_id: str
    smiles: str
    label: int
    target: str
    split: str


@dataclass(frozen=True)
class SimilarityResult:
    target: str
    method: str
    train_queries: int
    metrics: RankingMetrics

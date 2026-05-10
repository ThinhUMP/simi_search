"""Ranking metrics for virtual-screening benchmarks."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class RankingMetrics:
    compounds: int
    actives: int
    ef1: float
    ef5: float
    bedroc20: float
    roc_auc: float
    pr_auc: float
    top1_actives: int
    top5_actives: int


def _top_fraction_size(total: int, fraction: float) -> int:
    if total <= 0:
        return 0
    return max(1, math.ceil(total * fraction))


def enrichment_factor(labels: Sequence[int], fraction: float) -> tuple[float, int]:
    total = len(labels)
    actives = sum(labels)
    if total == 0 or actives == 0:
        return 0.0, 0
    top_k = _top_fraction_size(total, fraction)
    top_actives = sum(labels[:top_k])
    expected = top_k * (actives / total)
    return top_actives / expected if expected else 0.0, top_actives


def roc_auc(labels: Sequence[int], scores: Sequence[float]) -> float:
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        return 0.0

    pairs = sorted(zip(scores, labels), key=lambda item: item[0])
    rank_sum = 0.0
    rank = 1
    index = 0
    while index < len(pairs):
        end = index + 1
        while end < len(pairs) and pairs[end][0] == pairs[index][0]:
            end += 1
        average_rank = (rank + rank + (end - index) - 1) / 2.0
        rank_sum += average_rank * sum(label for _, label in pairs[index:end])
        rank += end - index
        index = end

    return (rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)


def pr_auc(labels: Sequence[int]) -> float:
    positives = sum(labels)
    if positives == 0:
        return 0.0

    area = 0.0
    true_positives = 0
    previous_recall = 0.0
    for rank, label in enumerate(labels, start=1):
        if label:
            true_positives += 1
            recall = true_positives / positives
            precision = true_positives / rank
            area += (recall - previous_recall) * precision
            previous_recall = recall
    return area


def bedroc(labels: Sequence[int], alpha: float = 20.0) -> float:
    """Compute BEDROC using the Truchon/Jain early-recognition formula."""

    total = len(labels)
    actives = sum(labels)
    if total == 0 or actives == 0 or actives == total:
        return 0.0

    active_ranks = [index for index, label in enumerate(labels, start=1) if label]
    rie_numerator = sum(math.exp(-alpha * rank / total) for rank in active_ranks)
    rie_denominator = (actives / total) * (1.0 - math.exp(-alpha)) / (math.exp(alpha / total) - 1.0)
    rie = rie_numerator / rie_denominator if rie_denominator else 0.0

    ratio = actives / total
    rie_max = (1.0 - math.exp(-alpha * ratio)) / (ratio * (1.0 - math.exp(-alpha)))
    rie_min = (1.0 - math.exp(alpha * ratio)) / (ratio * (1.0 - math.exp(alpha)))
    if rie_max == rie_min:
        return 0.0
    return max(0.0, min(1.0, (rie - rie_min) / (rie_max - rie_min)))


def compute_ranking_metrics(labels: Sequence[int], scores: Sequence[float]) -> RankingMetrics:
    ranked = sorted(zip(scores, labels), key=lambda item: item[0], reverse=True)
    ranked_scores = [score for score, _ in ranked]
    ranked_labels = [label for _, label in ranked]
    ef1, top1_actives = enrichment_factor(ranked_labels, 0.01)
    ef5, top5_actives = enrichment_factor(ranked_labels, 0.05)
    return RankingMetrics(
        compounds=len(ranked_labels),
        actives=sum(ranked_labels),
        ef1=ef1,
        ef5=ef5,
        bedroc20=bedroc(ranked_labels, alpha=20.0),
        roc_auc=roc_auc(ranked_labels, ranked_scores),
        pr_auc=pr_auc(ranked_labels),
        top1_actives=top1_actives,
        top5_actives=top5_actives,
    )

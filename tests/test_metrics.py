from __future__ import annotations

import unittest

from simi_search.metrics import compute_ranking_metrics, enrichment_factor, roc_auc


class MetricsTests(unittest.TestCase):
    def test_enrichment_factor_counts_top_fraction_actives(self) -> None:
        ef, top_actives = enrichment_factor([1, 0, 1, 0], 0.5)
        self.assertEqual(top_actives, 1)
        self.assertAlmostEqual(ef, 1.0)

    def test_roc_auc_handles_perfect_and_reversed_rankings(self) -> None:
        self.assertAlmostEqual(roc_auc([1, 0, 1, 0], [0.9, 0.2, 0.8, 0.1]), 1.0)
        self.assertAlmostEqual(roc_auc([1, 0, 1, 0], [0.1, 0.8, 0.2, 0.9]), 0.0)

    def test_compute_ranking_metrics_sorts_by_score(self) -> None:
        metrics = compute_ranking_metrics([0, 1, 0, 1], [0.1, 0.9, 0.2, 0.8])
        self.assertEqual(metrics.compounds, 4)
        self.assertEqual(metrics.actives, 2)
        self.assertEqual(metrics.top1_actives, 1)
        self.assertGreater(metrics.bedroc20, 0.0)
        self.assertAlmostEqual(metrics.roc_auc, 1.0)


if __name__ == "__main__":
    unittest.main()

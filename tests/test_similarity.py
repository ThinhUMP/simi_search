from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from simi_search.benchmark import LitPcbaTargetRepository, SimilarityBenchmarkRunner
from simi_search.fingerprints import HashedSmilesFingerprint, RdkitMorganFingerprint, build_fingerprinter
from simi_search.search import TanimotoSimilarity


class SimilarityTests(unittest.TestCase):
    def write_lit_pcba_csv(self, path: Path, rows: list[tuple[str, str, int, str]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["ID", "SMILES", "Real_Class", "Label", "Target", "Split"])
            writer.writeheader()
            for compound_id, smiles, label, split in rows:
                writer.writerow(
                    {
                        "ID": compound_id,
                        "SMILES": smiles,
                        "Real_Class": "Active" if label else "Inactive",
                        "Label": label,
                        "Target": "TEST",
                        "Split": split,
                    }
                )

    def test_tanimoto_on_integer_bitsets(self) -> None:
        similarity = TanimotoSimilarity()
        self.assertAlmostEqual(similarity.score(0b1110, 0b0111), 0.5)
        self.assertEqual(similarity.score(0, 0), 0.0)

    def test_hashed_fingerprint_is_deterministic(self) -> None:
        featurizer = HashedSmilesFingerprint(n_bits=128)
        self.assertEqual(featurizer.fingerprint("CCO"), featurizer.fingerprint("CCO"))
        self.assertNotEqual(featurizer.fingerprint("CCO"), featurizer.fingerprint("NNN"))

    def test_build_fingerprinter_resolves_supported_names(self) -> None:
        self.assertIsInstance(build_fingerprinter("hashed"), HashedSmilesFingerprint)
        self.assertIsInstance(build_fingerprinter("rdkit"), RdkitMorganFingerprint)

    def test_rdkit_fingerprint_when_rdkit_is_available(self) -> None:
        try:
            import rdkit  # noqa: F401
        except ImportError:
            self.skipTest("RDKit is not installed")

        featurizer = RdkitMorganFingerprint(n_bits=128)
        self.assertGreater(featurizer.fingerprint("CCO"), 0)
        with self.assertRaises(ValueError):
            featurizer.fingerprint("not-a-smiles")

    def test_benchmark_target_uses_train_actives_as_queries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "processed"
            target_dir = root / "TEST"
            self.write_lit_pcba_csv(
                target_dir / "TEST-LIT-PCBA-train.csv",
                [("q1", "CCO", 1, "train"), ("n1", "NNN", 0, "train")],
            )
            self.write_lit_pcba_csv(
                target_dir / "TEST-LIT-PCBA-validation.csv",
                [("v1", "CCO", 1, "validation"), ("v2", "NNN", 0, "validation")],
            )

            repository = LitPcbaTargetRepository(root)
            self.assertEqual(repository.discover_targets(), ["TEST"])
            result = SimilarityBenchmarkRunner(repository=repository).run_target("TEST")
            self.assertEqual(result.train_queries, 1)
            self.assertEqual(result.metrics.top1_actives, 1)
            self.assertAlmostEqual(result.metrics.roc_auc, 1.0)


if __name__ == "__main__":
    unittest.main()

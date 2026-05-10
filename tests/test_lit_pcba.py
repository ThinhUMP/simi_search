from __future__ import annotations

import csv
import tarfile
import tempfile
import unittest
from pathlib import Path

from simi_search.datasets.lit_pcba import (
    extract_archive,
    find_target_dirs,
    prepare_lit_pcba,
)


class LitPcbaTests(unittest.TestCase):
    def make_archive(self, tmpdir: Path) -> Path:
        source = tmpdir / "source" / "LIT-PCBA" / "ADRB2"
        source.mkdir(parents=True)
        (source / "active.smi").write_text("CCO SID1\nCCC SID2\n", encoding="utf-8")
        (source / "inactive.smi").write_text("NNN SID3\n", encoding="utf-8")
        (source / "active_T.smi").write_text("CCO SID1\n", encoding="utf-8")
        (source / "inactive_T.smi").write_text("NNN SID3\n", encoding="utf-8")
        (source / "active_V.smi").write_text("CCC SID2\n", encoding="utf-8")
        (source / "inactive_V.smi").write_text("", encoding="utf-8")

        archive = tmpdir / "fixture.tgz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(tmpdir / "source" / "LIT-PCBA", arcname="LIT-PCBA")
        return archive

    def test_prepare_lit_pcba_from_existing_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            archive = self.make_archive(tmpdir)

            output_dir, summaries = prepare_lit_pcba(
                data_dir=tmpdir / "data",
                archive_path=archive,
                skip_download=True,
            )

            summary_counts = {(summary.target, summary.split): summary.compounds for summary in summaries}
            self.assertEqual(summary_counts[("ADRB2", "all")], 3)
            self.assertEqual(summary_counts[("ADRB2", "train")], 2)
            self.assertEqual(summary_counts[("ADRB2", "validation")], 1)

            all_csv = output_dir / "ADRB2" / "ADRB2-LIT-PCBA-all.csv"
            with all_csv.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["ID"], "SID1")
            self.assertEqual(rows[0]["Real_Class"], "Active")
            self.assertEqual(rows[-1]["Label"], "0")
            self.assertTrue((output_dir / "manifest.json").exists())

    def test_find_target_dirs_detects_nested_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "nested" / "TP53"
            target.mkdir(parents=True)
            (target / "active.smi").write_text("CC SID\n", encoding="utf-8")

            self.assertEqual(find_target_dirs(root), [target.resolve()])

    def test_extract_archive_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            archive = tmpdir / "unsafe.tgz"
            payload = tmpdir / "payload.txt"
            payload.write_text("bad", encoding="utf-8")
            with tarfile.open(archive, "w:gz") as tar:
                tar.add(payload, arcname="../payload.txt")

            with self.assertRaises(ValueError):
                extract_archive(archive, tmpdir / "extract")


if __name__ == "__main__":
    unittest.main()

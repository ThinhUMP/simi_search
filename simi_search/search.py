"""OOP ligand similarity search implementations."""

from __future__ import annotations

from collections.abc import Sequence

from simi_search.fingerprints import Fingerprinter, HashedSmilesFingerprint
from simi_search.models import Molecule


class TanimotoSimilarity:
    """Tanimoto similarity over integer bitset fingerprints."""

    def score(self, left: int, right: int) -> float:
        if not left and not right:
            return 0.0
        intersection = (left & right).bit_count()
        union = (left | right).bit_count()
        return intersection / union if union else 0.0


class MaxActiveSimilaritySearch:
    """Score candidates by maximum similarity to active reference ligands."""

    def __init__(
        self,
        *,
        fingerprinter: Fingerprinter | None = None,
        method_name: str = "hashed_smiles",
        similarity: TanimotoSimilarity | None = None,
    ) -> None:
        self.fingerprinter = fingerprinter or HashedSmilesFingerprint()
        self.method_name = method_name
        self.similarity = similarity or TanimotoSimilarity()

    def score(self, queries: Sequence[Molecule], candidates: Sequence[Molecule]) -> list[float]:
        if not queries:
            raise ValueError("at least one active training query is required")

        query_fingerprints = [self.fingerprinter.fingerprint(molecule.smiles) for molecule in queries]
        scores: list[float] = []
        for candidate in candidates:
            candidate_fingerprint = self.fingerprinter.fingerprint(candidate.smiles)
            scores.append(
                max(
                    self.similarity.score(query_fingerprint, candidate_fingerprint)
                    for query_fingerprint in query_fingerprints
                )
            )
        return scores

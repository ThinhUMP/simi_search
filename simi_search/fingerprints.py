"""Fingerprint implementations for ligand similarity search."""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from collections.abc import Iterable


class Fingerprinter(ABC):
    """Interface for molecule featurizers used by similarity search."""

    @abstractmethod
    def fingerprint(self, smiles: str) -> int:
        raise NotImplementedError


class HashedSmilesFingerprint(Fingerprinter):
    """Dependency-free hashed token fingerprint for SMILES similarity."""

    def __init__(self, *, n_bits: int = 2048, min_ngram: int = 2, max_ngram: int = 4) -> None:
        if n_bits <= 0:
            raise ValueError("n_bits must be positive")
        if min_ngram <= 0 or max_ngram < min_ngram:
            raise ValueError("invalid n-gram bounds")
        self.n_bits = n_bits
        self.min_ngram = min_ngram
        self.max_ngram = max_ngram

    def fingerprint(self, smiles: str) -> int:
        normalized = smiles.strip()
        bitset = 0
        for token in self._tokens(normalized):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            bitset |= 1 << (int.from_bytes(digest, "big") % self.n_bits)
        return bitset

    def _tokens(self, smiles: str) -> Iterable[str]:
        padded = f"^{smiles}$"
        yielded = False
        for size in range(self.min_ngram, self.max_ngram + 1):
            if len(padded) < size:
                continue
            for index in range(0, len(padded) - size + 1):
                yielded = True
                yield padded[index : index + size]
        if not yielded and smiles:
            yield smiles


class RdkitMorganFingerprint(Fingerprinter):
    """RDKit Morgan/ECFP bit-vector fingerprinter.

    RDKit is optional so the base package remains lightweight. Install it with
    ``pip install "simi-search[rdkit]"`` or ``conda install -c conda-forge rdkit``.
    """

    def __init__(self, *, radius: int = 2, n_bits: int = 2048) -> None:
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if n_bits <= 0:
            raise ValueError("n_bits must be positive")
        self.radius = radius
        self.n_bits = n_bits

    def fingerprint(self, smiles: str) -> int:
        try:
            from rdkit import Chem
            from rdkit.Chem import rdFingerprintGenerator
        except ImportError as error:
            raise ImportError(
                "RDKit is required for RdkitMorganFingerprint. "
                'Install with `pip install "simi-search[rdkit]"` or `conda install -c conda-forge rdkit`.'
            ) from error

        molecule = Chem.MolFromSmiles(smiles)
        if molecule is None:
            raise ValueError(f"Invalid SMILES for RDKit fingerprinting: {smiles!r}")

        generator = rdFingerprintGenerator.GetMorganGenerator(radius=self.radius, fpSize=self.n_bits)
        fingerprint = generator.GetFingerprint(molecule)
        bitset = 0
        for bit in fingerprint.GetOnBits():
            bitset |= 1 << bit
        return bitset


def build_fingerprinter(name: str) -> Fingerprinter:
    """Create a supported fingerprinter by CLI/config name."""

    normalized = name.strip().lower().replace("_", "-")
    if normalized in {"hashed", "hashed-smiles", "smiles"}:
        return HashedSmilesFingerprint()
    if normalized in {"rdkit", "morgan", "ecfp", "rdkit-morgan"}:
        return RdkitMorganFingerprint()
    raise ValueError(f"Unknown fingerprint method {name!r}; choose 'hashed' or 'rdkit'.")

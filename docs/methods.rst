Methods
=======

Simi Search evaluates ligand-based retrieval through three linked stages:
dataset standardization, similarity scoring, and enrichment analysis.

Dataset Preparation
-------------------

The downloader converts official LIT-PCBA SMILES files into normalized CSV
files:

.. code-block:: text

   ID,SMILES,Real_Class,Label,Target,Split

``Label=1`` denotes an active molecule and ``Label=0`` denotes an inactive
molecule. The processed directory follows this layout:

.. code-block:: text

   data/processed/lit_pcba_ave/
     PPARG/
       PPARG-LIT-PCBA-train.csv
       PPARG-LIT-PCBA-validation.csv

Similarity Retrieval
--------------------

For each target, the benchmark follows a held-out retrieval protocol:

#. Select active molecules from the training split.
#. Read all molecules from the validation split.
#. Fingerprint every molecule from its SMILES string.
#. Compute Tanimoto similarity between each validation molecule and every active
   training molecule.
#. Assign each validation molecule its maximum active-query similarity.
#. Rank validation molecules by decreasing score.
#. Compute enrichment and ranking metrics from validation labels.

Default Fingerprint
-------------------

Simi Search supports two fingerprint backends:

``HashedSmilesFingerprint``
   Dependency-free deterministic integer bitsets from hashed SMILES n-grams.
   This is the lightweight baseline.

``RdkitMorganFingerprint``
   RDKit Morgan/ECFP fingerprints converted into the same integer bitset
   representation used by the search engine. Install with
   ``pip install "simi-search[rdkit]"`` or ``conda install -c conda-forge rdkit``.

.. code-block:: python

   from simi_search.fingerprints import HashedSmilesFingerprint, RdkitMorganFingerprint

   fingerprinter = HashedSmilesFingerprint(n_bits=2048)
   bitset = fingerprinter.fingerprint("CCO")

   rdkit_fingerprinter = RdkitMorganFingerprint(radius=2, n_bits=2048)
   rdkit_bitset = rdkit_fingerprinter.fingerprint("CCO")

Extension Point
---------------

Future molecular representations should implement the same contract:

.. code-block:: python

   class Fingerprinter:
       def fingerprint(self, smiles: str) -> int:
           ...

This keeps benchmark orchestration unchanged when adding learned molecular
embeddings or other molecular fingerprints.

Metrics
-------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Metric
     - Interpretation
   * - ``EF1%``
     - Enrichment factor in the top one percent of the ranked library.
   * - ``EF5%``
     - Enrichment factor in the top five percent of the ranked library.
   * - ``BEDROC20``
     - Early-recognition score with alpha 20.
   * - ``ROC_AUC``
     - Overall pairwise ranking quality.
   * - ``PR_AUC``
     - Precision-recall area for imbalanced active/inactive screens.

Interpretation
--------------

Early enrichment should drive method selection. A method that improves
``ROC_AUC`` but fails to improve ``EF1%`` or ``BEDROC20`` may still be weak for
practical virtual screening, where the top-ranked compounds matter most.

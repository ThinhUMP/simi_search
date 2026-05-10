Simi Search
===============

**Simi Search**: a ligand-similarity benchmark for LIT-PCBA virtual
screening.

Simi Search provides a focused framework for preparing LIT-PCBA, running
ligand-only retrieval, and evaluating early enrichment. The benchmark
deliberately excludes docking, protein-ligand interaction fingerprints, random
forest scores, CNN scores, and consensus scoring so the effect of ligand
similarity can be measured directly.

Abstract
--------

Ligand-based virtual screening is often used when structural models, docking
poses, or target-specific scoring functions are unavailable or expensive to
produce. However, similarity search can be overstated when benchmarks contain
analogue bias or when evaluation focuses on global ranking statistics rather
than early enrichment. Simi Search addresses this by using the
AVE-unbiased LIT-PCBA benchmark and by ranking validation compounds according
to their maximum Tanimoto similarity to active training ligands. The package
standardizes dataset preparation, scoring, and evaluation so future molecular
fingerprints can be compared against a transparent hashed-SMILES baseline.

Framework Overview
------------------

.. raw:: html

   <div class="framework-strip">
     <div class="framework-node">
       <span class="node-index">1</span>
       <strong>LIT-PCBA</strong>
       <p>Download AVE-unbiased target splits from the official archive.</p>
     </div>
     <div class="framework-arrow">→</div>
     <div class="framework-node">
       <span class="node-index">2</span>
       <strong>Normalize</strong>
       <p>Convert active and inactive SMILES files into target CSV files.</p>
     </div>
     <div class="framework-arrow">→</div>
     <div class="framework-node">
       <span class="node-index">3</span>
       <strong>Search</strong>
       <p>Rank validation compounds by max similarity to train actives.</p>
     </div>
     <div class="framework-arrow">→</div>
     <div class="framework-node">
       <span class="node-index">4</span>
       <strong>Evaluate</strong>
       <p>Report EF1%, EF5%, BEDROC20, ROC_AUC, and PR_AUC.</p>
     </div>
   </div>

Benchmark Design
----------------

.. list-table::
   :header-rows: 1
   :widths: 28 34 38

   * - Benchmark component
     - Implementation
     - Scientific rationale
   * - Dataset
     - LIT-PCBA AVE-unbiased
     - HTS-derived targets with reduced analogue bias.
   * - Query/reference set
     - Active training molecules
     - Known ligands define the target-specific similarity query set.
   * - Screening set
     - Validation molecules
     - Held-out compounds are ranked without using validation labels.
   * - Similarity score
     - Maximum Tanimoto to any active training molecule
     - Nearest-active retrieval baseline for ligand-based screening.
   * - Fingerprints
     - Hashed SMILES n-grams and optional RDKit Morgan/ECFP
     - Lightweight default plus chemistry-aware RDKit backend.
   * - Primary metrics
     - EF1%, EF5%, BEDROC20
     - Early-recognition metrics aligned with practical virtual screening.

Evaluation Pillars
------------------

.. raw:: html

   <div class="grid-cards">
     <a class="doc-card" href="methods.html#similarity-retrieval">
       <h3>Similarity Retrieval</h3>
       <p>Fingerprint SMILES and rank validation molecules by max-active Tanimoto similarity.</p>
     </a>
     <a class="doc-card" href="methods.html#metrics">
       <h3>Early Enrichment</h3>
       <p>Use EF1%, EF5%, and BEDROC20 as the primary virtual-screening readouts.</p>
     </a>
     <a class="doc-card" href="api.html">
       <h3>Extensible API</h3>
       <p>Use the hashed baseline, RDKit Morgan fingerprints, or custom fingerprinters.</p>
     </a>
   </div>

Explore the Documentation
-------------------------

.. raw:: html

   <div class="grid-cards">
     <a class="doc-card" href="usage.html">
       <h3>Getting Started</h3>
       <p>Install the package, prepare LIT-PCBA, and run a target benchmark.</p>
     </a>
     <a class="doc-card" href="methods.html">
       <h3>Methods</h3>
       <p>Understand dataset handling, fingerprinting, retrieval, and metrics.</p>
     </a>
     <a class="doc-card" href="release.html">
       <h3>Release</h3>
       <p>Publish PyPI, conda, and Docker artifacts from GitHub Actions.</p>
     </a>
   </div>

.. toctree::
   :maxdepth: 2
   :caption: Documentation
   :hidden:

   usage
   methods
   api
   release

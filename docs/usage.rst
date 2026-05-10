Getting Started
===============

Installation
------------

Choose the installation method that matches your workflow.

Option 1: PyPI
~~~~~~~~~~~~~~

.. code-block:: bash

   pip install simi-search

Option 2: Source checkout
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/ThinhUMP/simi_search.git
   cd simi_search
   python -m pip install -r requirements.txt

Optional RDKit fingerprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install "simi-search[rdkit]"

or, in conda environments:

.. code-block:: bash

   conda install -c conda-forge rdkit

Option 3: Docker image
~~~~~~~~~~~~~~~~~~~~~~

The release workflow publishes a container to GitHub Container Registry:

.. code-block:: bash

   docker pull ghcr.io/thinhump/simi_search:latest

Run the benchmark command inside the image with a mounted workspace:

.. code-block:: bash

   docker run --rm \
     -v "$PWD/data:/app/data" \
     -v "$PWD/results:/app/results" \
     ghcr.io/thinhump/simi_search:latest \
     --data-dir data/processed/lit_pcba_ave \
     --output results/lit_pcba_similarity_metrics.csv

Quick Example
-------------

Prepare the AVE-unbiased LIT-PCBA benchmark:

.. code-block:: bash

   download-lit-pcba --data-dir data --variant ave

Run a single-target similarity benchmark:

.. code-block:: bash

   benchmark-similarity \
     --data-dir data/processed/lit_pcba_ave \
     --target PPARG \
     --output results/PPARG_similarity_metrics.csv

Run the same target with RDKit Morgan fingerprints:

.. code-block:: bash

   benchmark-similarity \
     --data-dir data/processed/lit_pcba_ave \
     --target PPARG \
     --fingerprint rdkit \
     --output results/PPARG_rdkit_similarity_metrics.csv

Run all processed targets:

.. code-block:: bash

   benchmark-similarity \
     --data-dir data/processed/lit_pcba_ave \
     --output results/lit_pcba_similarity_metrics.csv

Output Schema
-------------

The benchmark writes one row per target:

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Column
     - Description
   * - ``Target``
     - LIT-PCBA target identifier.
   * - ``Method``
     - Similarity scoring method.
   * - ``Train_Queries``
     - Number of active training ligands used as references.
   * - ``Compounds``
     - Number of validation compounds ranked.
   * - ``Actives``
     - Number of active validation compounds.
   * - ``EF1%`` / ``EF5%``
     - Enrichment factors in the top 1% and 5%.
   * - ``BEDROC20``
     - Early-recognition metric with alpha 20.
   * - ``ROC_AUC`` / ``PR_AUC``
     - Global ranking and precision-recall metrics.

Next Steps
----------

* Read :doc:`methods` for the benchmark protocol.
* Read :doc:`api` to extend the fingerprinter or searcher classes.
* Read :doc:`release` before publishing package artifacts.

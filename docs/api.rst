API Reference
=============

Benchmark orchestration
-----------------------

.. automodule:: simi_search.benchmark
   :members:
   :undoc-members:
   :show-inheritance:

Fingerprints
------------

.. automodule:: simi_search.fingerprints
   :members:
   :undoc-members:
   :show-inheritance:

Fingerprint selection
~~~~~~~~~~~~~~~~~~~~~

The command line exposes the same backends as the Python API:

.. code-block:: bash

   benchmark-similarity --fingerprint hashed
   benchmark-similarity --fingerprint rdkit

``rdkit`` uses Morgan fingerprints and requires RDKit to be installed.

Similarity search
-----------------

.. automodule:: simi_search.search
   :members:
   :undoc-members:
   :show-inheritance:

Metrics
-------

.. automodule:: simi_search.metrics
   :members:
   :undoc-members:
   :show-inheritance:

Models
------

.. automodule:: simi_search.models
   :members:
   :undoc-members:
   :show-inheritance:

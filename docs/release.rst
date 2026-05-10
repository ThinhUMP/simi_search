Release
=======

Versioning
----------

Before creating a release, update the version in:

* ``pyproject.toml``
* ``simi_search/__init__.py``
* ``conda-recipe/meta.yaml``
* ``docs/conf.py``

PyPI
----

The ``Release PyPI`` GitHub Actions workflow builds the source distribution and
wheel, then publishes them through PyPI trusted publishing.

Repository setup:

* Configure a PyPI trusted publisher for this repository.
* Keep the ``pypi`` GitHub environment if release approval is desired.

Conda
-----

The ``Release Conda`` workflow builds ``conda-recipe/meta.yaml`` and uploads the
package with ``anaconda-client``.

Repository setup:

* Add ``ANACONDA_API_TOKEN`` as a GitHub Actions secret.
* Ensure ``ANACONDA_API_TOKEN`` has upload permission for the target channel.

Docker
------

The ``Release Docker`` workflow publishes the package image to GitHub Container
Registry:

.. code-block:: text

   ghcr.io/thinhump/simi_search

The image entrypoint is ``benchmark-similarity``.

Dependabot
----------

Dependabot checks GitHub Actions, Docker, and Python packaging metadata weekly.

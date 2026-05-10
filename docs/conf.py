"""Sphinx configuration for Simi Search documentation."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

project = "Simi Search"
author = "ThinhUMP"
copyright = f"{datetime.now(UTC).year}, {author}"
release = "0.1.0"
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["scientific.css"]
html_title = "Simi Search"
html_logo = "_static/logo.svg"
html_favicon = "_static/logo.svg"
html_show_sourcelink = False
html_context = {
    "display_github": True,
    "github_user": "ThinhUMP",
    "github_repo": "simi_search",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = True

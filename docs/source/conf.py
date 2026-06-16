# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

import os
import sys
import subprocess
import shutil
from importlib.metadata import version as _pkg_version

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../..'))


# -- Project information -----------------------------------------------------

project = 'SDyPy - Structural Dynamics Scientific Python'
copyright = '2020, SDyPy Consortium'
author = 'Janko Slavič, Domen Gorjup, Klemen Zaletelj, Tomaž Bregar'

# The full version, including alpha/beta/rc tags, from installed metadata
release = _pkg_version("sdypy")
# The short X.Y version
version = ".".join(release.split(".")[:2])


# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
]

# autodoc: mock heavy optional backends so the build doesn't need Qt / pyvista
autodoc_mock_imports = ["PyQt6", "pyvistaqt"]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

language = 'en'

exclude_patterns = []

pygments_style = None


# -- Options for HTML output -------------------------------------------------

html_theme = 'pydata_sphinx_theme'

html_theme_options = {
    "github_url": "https://github.com/sdypy/sdypy",
    "show_prev_next": True,
    "external_links": [
        {"name": "sdypy-EMA docs", "url": "https://sdypy-ema.readthedocs.io/en/latest/"},
        {"name": "sdypy-io docs",  "url": "https://sdypy-io.readthedocs.io/en/latest/"},
        {"name": "sdypy-FRF docs", "url": "https://pyfrf.readthedocs.io/en/latest/"},
        {"name": "sdypy-excitation docs", "url": "https://pyexsi.readthedocs.io/en/latest/"},
        {"name": "sdypy-view docs", "url": "https://sdypy-view.readthedocs.io/en/latest/"},
        {"name": "sdypy-model docs", "url": "https://sdypy-model.readthedocs.io/en/latest/"},
    ],
}

html_static_path = ['_static']

htmlhelp_basename = 'sdypy'


# -- Intersphinx mapping -----------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {}

latex_documents = [
    (master_doc, 'sdypy.tex', 'SDyPy Documentation',
     'SDyPy Consortium', 'manual'),
]


# -- Options for manual page output ------------------------------------------

man_pages = [
    (master_doc, 'sdypy', 'SDyPy Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

texinfo_documents = [
    (master_doc, 'SDyPy', 'SDyPy Documentation',
     author, 'SDyPy', 'Structural Dynamics Python.',
     'Miscellaneous'),
]


# -- Options for Epub output -------------------------------------------------

epub_title = project
epub_exclude_files = ['search.html']


# -- SEP integration hook ----------------------------------------------------
# At build time: regenerate the SEP index and copy SEP .rst files into
# docs/source/seps/ so the umbrella toctree can reference them.

_here = os.path.dirname(os.path.abspath(__file__))
_seps = os.path.normpath(os.path.join(_here, '..', 'seps'))
try:
    subprocess.run(
        [sys.executable, os.path.join('tools', 'build_index.py')],
        cwd=_seps,
        check=True,
    )
except Exception as _e:
    print('SEP index generation skipped:', _e)

_dst = os.path.join(_here, 'seps')
os.makedirs(_dst, exist_ok=True)
# 'content.rst' is the master_doc for the standalone SEP Sphinx project;
# it must NOT be copied into the umbrella build.
_SKIP = {'content.rst'}
for _fn in os.listdir(_seps):
    if _fn.endswith('.rst') and _fn not in _SKIP:
        shutil.copy(os.path.join(_seps, _fn), os.path.join(_dst, _fn))

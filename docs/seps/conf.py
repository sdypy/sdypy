# -*- coding: utf-8 -*-
#
# SDyPy Enhancement Proposals documentation build configuration file.
#
# This file is execfile()d with the current directory set to its
# containing dir.

import os


# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.imgmath',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
]

templates_path = ['_templates/']

source_suffix = '.rst'

master_doc = 'content'

project = 'SDyPy Enhancement Proposals'
copyright = '2020-2024, SDyPy Developers'
author = 'SDyPy Developers'

version = u''
release = u''

language = 'en'

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'

todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

html_theme = 'pydata_sphinx_theme'

html_theme_options = {
    "github_url": "https://github.com/sdypy/sdypy",
    "show_prev_next": False,
    "external_links": [
        {"name": "Wish List",
         "url": "https://github.com/sdypy/sdypy/issues?q=is%3Aopen+is%3Aissue+label%3A%2223+-+Wish+list%22",
         },
    ],
}

html_title = "%s" % (project)
html_static_path = ['../source/_static']
html_last_updated_fmt = '%b %d, %Y'

html_use_modindex = True
html_copy_source = False
html_domain_indices = False
html_file_suffix = '.html'


# -- Options for HTMLHelp output ------------------------------------------

htmlhelp_basename = 'sdypy-seps'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

latex_documents = [
    (master_doc, 'SDyPyEnhancementProposals.tex',
     u'SDyPy Enhancement Proposals Documentation',
     u'SDyPy Developers', 'manual'),
]


# -- Options for manual page output ---------------------------------------

man_pages = [
    (master_doc, 'sdypyenhancementproposals',
     u'SDyPy Enhancement Proposals Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

texinfo_documents = [
    (master_doc, 'SDyPyEnhancementProposals',
     u'SDyPy Enhancement Proposals Documentation',
     author, 'SDyPyEnhancementProposals',
     'SDyPy Enhancement Proposals — design documents for the SDyPy ecosystem.',
     'Miscellaneous'),
]


# -- Intersphinx configuration --------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
}

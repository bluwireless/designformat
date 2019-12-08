# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
doc_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(doc_dir, '../../python'))

# -- Project information -----------------------------------------------------

project = 'Design Format'
copyright = '2019, Blu Wireless'
author = 'Blu Wireless'

# The full version, including alpha/beta/rc tags
release = '1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # Native Sphinx extensions
    'sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.napoleon',
    # Enable Markdown support via Recommonmark
    'recommonmark', 'sphinx_markdown_tables',
    # SphinxJS for Javascript library documentation
    'sphinx_js'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# Source code path for Javascript library
js_source_path = os.path.join(doc_dir, '../../javascript')

# Set the root document
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Setup for enabling RST evaluation within MD -----------------------------
from recommonmark.transform import AutoStructify
def setup(app):
    app.add_config_value('recommonmark_config', {
        # 'auto_toc_tree_section': 'Contents',
        'enable_eval_rst'      : True,
        # 'enable_auto_doc_ref'  : True
    }, True)
    app.add_transform(AutoStructify)
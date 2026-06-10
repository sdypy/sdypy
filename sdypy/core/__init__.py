"""Reserved core namespace for the umbrella sdypy package.

Intentionally minimal. The package version is sourced from the installed
distribution metadata via importlib.metadata in sdypy/__init__.py and is no
longer defined here. This module is kept only to preserve the 'import sdypy.core'
surface for anything that relies on it.
"""

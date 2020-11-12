SDyPy - Structural Dynamics Python development notes
----------------------------------------------------

To download the source code:

.. code-block:: console

    $ git clone https://github.com/sdypy/sdypy


To begin development, install the required packages with :

.. code-block:: console

    $ python -m pip install -r requirements.dev.txt


Consider adding unit-tests in ``tests/``. The provided test file structure is setup to work with `pytest <https://docs.pytest.org/en/latest/>`_.

To also use the sphinx documentation, modify files in ``docs/source`` (see `Sphinx - Getting started <https://www.sphinx-doc.org/en/master/usage/quickstart.html>`_ for more info).


File structure
--------------

The project code is structured as follows:

setup.py
    the Python setup script, used to package the project

requirements.txt
    a list of packages, required to use this project
    
requirements.dev.txt
    a list of packages, required to develop this project

README.rst
    the main projecdt description / documentation file

CONTRIBUTING.rst
    a document containing information for potential contrubutors (developers) of the package

License
    the project License

.travis.yml
    contains the set of instructions to run wit the `TravisCI <https://travis-ci.org/>`_ continuous integration service after the file repository has been updated

.gitignore
    defines the files in the project directory to be excluded from version control

tests/
    contains project unit-tests

sdypy/
    contains the core project source code, separated into meaningful sub-modules

examples/
    scripts, notebooks with examples to showcase the project

docs/
    the documentation source and built files



Building the documentation
--------------------------

By setting up `ReadTheDocs <https://readthedocs.org/>`_, your project documentation can automatically be built and puclished as a publicly available website.

To test your documentation locally, run the following (starting from the main project directory) :

.. code-block:: console

    $ cd docs
    $ make clean
    $ make html

Your documentation files will be built inside the ``docs/build/html`` folder.


Publishing the project
----------------------

You can build your project and publish it to the `Python Package Index <https://pypi.org/>`_ with the following basic steps:

1. Build you project source code :

.. code-block:: console

    $ python setup.py sdist bdist_wheel

The built project can be tested locally by installing the resulting ``.whl`` file, found in the ``dist/`` folder  in a new virtual environemtn:

.. code-block:: console

    $ python -m virtualenv venv
    $ venv/Scripts/activate
    $ python -m pip install <sdypy-#>.whl 

(replace ``<sdypy-#>`` above with the actual ``.whl`` file name).

2. Upload the distribution files from ``dist/`` to PyPI :

.. code-block:: console

    $ python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

(``--repository-url https://test.pypi.org/legacy/`` uploads the package to the test PyPI for testing. To publish you package to the main PyPI repository, simply ommit this option from the above command.)

For more information on the publishng process, see this simpel `Python packaging tutorial <https://packaging.python.org/tutorials/packaging-projects/>`_.

3. After that,  the SDyPy will be available on PyPI and can be installed with `pip <https://pip.pypa.io>`_.

.. code-block:: console

    $ pip install sdypy

After installing SDyPy you can use it like any other Python module.

Here is a simple example with the current example code:

.. code-block:: python

    import sdypy as sd
    import numpy as np
    import matplotlib.pyplot as plt

    print(sd.__version__)

You can also run this basic example by running the following command in the project base direcotry:

.. code-block:: console

    $ python -m examples.basic_example

The `Read the Docs page <http://sdypy.readthedocs.io>`_ provides the project documentation.

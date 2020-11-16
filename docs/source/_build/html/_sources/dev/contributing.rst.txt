Contributing Guide
==================

Contributions are welcome and greatly appreciated!


.. _contributing-workflow-label:

Workflow
--------

A bug-fix or enhancement is delivered using a pull request. A good pull request
should cover one bug-fix or enhancement feature. This ensures the change set is
easier to review and less likely to need major re-work or even be rejected.

The workflow that developers typically use to fix a bug or add enhancements
is as follows.

* Fork the ``sdypy`` repo into your account.

* Obtain the source by cloning it onto your development machine.

  .. code-block:: console

      $ git clone ttps://github.com/sdypy/sdypy.git
      $ cd sdypy

* Create a branch for local development:

  .. code-block:: console

      $ git checkout -b name-of-your-bugfix-or-feature

  Now you can make your changes locally.


* Develop fix or enhancement:

  * Make a fix or enhancement (e.g. modify a class, method, function, module,
    etc).

  * Update an existing unit test or create a new unit test module to verify
    the change works as expected.

  * Run the test suite.

    .. code-block:: console

        $ pytest


* The docs should be updated for anything but trivial bug fixes. 


Perform docs check.

    .. code-block:: console

        $ cd docs
        $ make clean
        $ make html


* Commit and push changes to your fork.

  .. code-block:: console

      $ git add .
      $ git commit -m "A detailed description of the changes."
      $ git push origin name-of-your-bugfix-or-feature

  A pull request should preferably only have one commit upon the current
  master HEAD, (via rebases and squash).

* Submit a pull request through the service website (e.g. Github, Gitlab).

* Check automated continuous integration steps all pass. Fix any problems
  if necessary and update the pull request.

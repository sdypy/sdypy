PEP8 and SDyPy
==============

All SDyPy Python code should adhere to `PEP8`_ style guidelines. It’s so
important that some continuous integration tests on GitHub will fail due
to certain PEP8 violations. Here are a few tips for ensuring PEP8
compliance before pushing your code:

-  Many integrated development environments (IDEs) have options that
   automatically check for PEP8 compliance. In Spyder, for example,
   `enable Real-time code style analysis`_ in Tools |rarr| Preferences |rarr|
   Editor |rarr| Code Introspection/Analysis and "Automatically remove
   trailing spaces when saving files" in in Tools |rarr| Preferences |rarr|
   Editor |rarr| Advanced Settings. This can help you fix PEP8 issues as you
   write your code.

-  You can also perform checks using the |flake8|_ tool. 

-  If you have existing code with a lot of PEP8 issues, consider using
   |autopep8|_ to automatically fix most of them.

.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _enable Real-time code style analysis: https://stackoverflow.com/questions/51463223/how-to-use-pep8-module-using-spyder

.. |flake8| replace:: ``flake8``
.. _flake8: http://flake8.pycqa.org/en/latest/

.. |autopep8| replace:: ``autopep8``
.. _autopep8: https://pypi.org/project/autopep8/0.8/


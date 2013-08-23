Contributing
============

Contributions of code and documentation are always welcome!


Submitting Issues
-----------------

Issues are easier to reproduce and resolve when they include:

- A pull request with a failing test demonstrating the issue (no need to file
  both a pull request and an issue, the pull request is sufficient).
- A code example that produces the issue consistently
- A traceback (when applicable)


Pull Requests
-------------

When creating a pull request, try to:

- Write tests that fail before your change and pass after it
- Note important changes in the `CHANGES`_ file
- Update the `README`_ file as needed
- Add yourself to the `AUTHORS`_ file

.. _AUTHORS: AUTHORS.rst
.. _CHANGES: CHANGES.rst
.. _README: README.rst


Testing
-------

Please add tests for your code and ensure existing tests don't break.  To run
the tests against your code::

    python setup.py test

You can use `tox`_ to test the code against supported Python and Django
versions.  First install tox::

    pip install tox

To run tests using tox::

    tox

To fully run the tests via tox, you must have python2.6, python2.7, and
python3.3 interpreters on your system, available by those names. If you are
missing one or more interpreters, tox will skip testing against that Python
version and notify you.

When submitting a pull request, please note whether you've run the tests with
tox (and against which versions). Before a pull request can be merged, all
tests must pass on all configured tox environments.

.. _tox: http://tox.readthedocs.org/en/latest/

pymmd
============

Python wrapper for `MultiMarkdown <https://github.com/fletcher/MultiMarkdown-5>`_, which converts MultiMarkdown flavored text into one of several outputs formats. This package directly wraps the reference implementation, and provides a simple interface to the library.

The `ctypes <https://docs.python.org/2/library/ctypes.html>`_ package is used to wrap libMultiMarkdown in a portable fashion.

Installation
=============

This package requires MultiMarkdown installed as a shared library in order to function. Currently, this can be installed by installing MultiMarkdown from `this <https://github.com/fletcher/MultiMarkdown-5/tree/develop>`_ branch, and installing the package with the shared option enabled. This installs the shared library version of libMultiMarkdown which can be called by this wrapper.

Once the shared library is installed, this package can be installed via pypi:

.. code:: bash

  pip install pymmd

Verifying the package is working as intended can be accomplished via a simple test command, which should print out the MultiMarkdown version in use:

.. code:: bash

  python -c "import pymmd; print(pymmd.version())"

Examples
=============

Converting a string of MultiMarkdown directly to various outputs:

.. code:: python

  import pymmd
  # Generate string of MultiMarkdown text named data

  html_output = pymmd.convert(data)
  latex_output = pymmd.convert(data, fmt=pymmd.LATEX)

  #Generate a snippet
  html_snippet = pymmd.convert(data, ext=pymmd.SNIPPET)

Files can also be converted directly, which enables the `Transclusion <http://fletcher.github.io/MultiMarkdown-5/transclusion>`_ capabilities of MultiMarkdown.

.. code:: python

  import pymmd

  #MMD file named data.mmd

  html_output = pymmd.convert_from("./data.mmd")
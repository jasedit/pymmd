pymmd
============

Python wrapper for `MultiMarkdown <https://github.com/fletcher/MultiMarkdown-5>`, which converts MultiMarkdown flavored text into one of several outputs formats. This package directly wraps the reference implementation, and provides a simple interface to the library.

The `ctypes <https://docs.python.org/2/library/ctypes.html>` package is used to wrap libMultiMarkdown in a portable fashion.

Installation
=============

This package requires MultiMarkdown installed as a shared library in order to function. Currently, this can be installed by installing MultiMarkdown from `this <https://github.com/jasedit/MultiMarkdown-5/tree/make_shared>` fork, and following the installation instructions.

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

Files can also be converted directly, which enables the `Transclusion <http://fletcher.github.io/MultiMarkdown-5/transclusion>` capabilities of MultiMarkdown.

.. code:: python

  import pymmd

  #MMD file named data.mmd

  html_output = pymmd.convert_from("./data.mmd")
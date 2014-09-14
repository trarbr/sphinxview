README
======

Automatically rebuild your Sphinx project on changes.

sphinxview is a Sphinx extension which shortens the feedback loop while working
on a Sphinx project. When used, it starts a local webserver and serves your
project so you can navigate around it. Whenever you make changes to the source
file matching the page currently displayed in the browser, the entire project
is automaticly rebuilt and your browser reloads the page when the new
build has finished.

Getting it
----------

You can install sphinxview from PyPI using pip:

   $ pip install sphinxview

Or you can get the source from the `GitHub repository
<https://github.com/trarbr/sphinxview>`_.

Using it
--------

Before you can use sphinxview, you must first enable it in the conf.py for
your Sphinx project. This is done by adding `sphinxview.ext` to the list
`extensions`::

   # conf.py
   extensions = ['sphinxview.ext']

Now you can use sphinxview to rebuild your project on changes to the source
files:

   $ sphinxview /path/to/your-sphinx-project/

To see additional options, run:

   $ sphinxview --help

About
-----

Sphinxview consists of three components:

`sphinxview/ext.py` is a Sphinx extension that adds `sphinxview.js` to all
HTML files built by Sphinx. To enable the extension, add `'sphinxview.ext'` to
the extensions list in your conf.py.

`sphinxview/sphinxview.js` is a piece of javascript that sends a request to the
HTTP server with name and build time of the HTML file it is embedded in.

`sphinxview/sphinxview.py` is a CLI program that starts a HTTP server and
rebuilds your project on changes to the files requested by `sphinxview.js`.
Your browser automatically refreshes when the new build is finished.


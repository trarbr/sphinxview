README
======

automatically rebuild your Sphinx project on changes

Warning: Alpha quality!

To test the extension::

   $ python sphinxview.py test-project/

`sphinxview.py` doubles as a Sphinx extension and a CLI program that serves and
rebuilds your project on changes. `sphinxview.py` must be enabled in your
conf.py.

`sphinxview.js` is a piece of javascript that is added to all built HTML pages
when the sphinxview extension is enabled. `sphinxview.js` should be placed in
your projects _static directory.

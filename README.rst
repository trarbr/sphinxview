README
======

automatically rebuild your Sphinx project on changes

Warning: Alpha quality!

To test the extension::

   $ python sphinxview-serve.py -b test-project/_build/ -s test-project/

`sphinxview.py` is the actual extension that you put in your Sphinx projects
conf.py.

`sphinxview.js` is a piece of javascript that is added to all HTML pages when
the sphinxview extension is enabled. `sphinxview.js` should be placed in your
projects _static directory.

`sphinxview-serve.py` contains all the magic:

* the server and its request handler
* a convenient commandline script for ease of use

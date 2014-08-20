#! /usr/bin/env python3
"""
This is the sphinxview extension

See http://sphinx-doc.org/config.html#confval-extensions for how to load
"""

# TODO: Place javascript file in _static
# https://bitbucket.org/birkenfeld/sphinx/src/b982ca5c7eb91f855c406c8ec610797ea61611dc/sphinx/ext/jsmath.py?at=default


def builder_inited(app):
    if app.config.sphinxview_enabled:
        app.add_javascript('sphinxview.js')


def setup(app):
    app.add_config_value('sphinxview_enabled', False, False)
    app.connect('builder-inited', builder_inited)

#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2014 Troels Brødsgaard
# License: 2-clause BSD, see LICENSE for details


def builder_inited(app):
    if app.config.sphinxview_enabled:
        app.add_javascript('sphinxview.js')


def setup(app):
    app.add_config_value('sphinxview_enabled', False, False)
    app.connect('builder-inited', builder_inited)

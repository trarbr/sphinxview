#! /usr/bin/env python3

# Copyright 2014 Troels Brødsgaard
# License: 2-clause BSD, see LICENSE for details

"""
sphinxview - serves your Sphinx project and reloads pages on source changes

Usage:
    sphinxview [options] <sourcedir>
    sphinxview -h | -- help

<sourcedir> must be a path to a valid Sphinx source directory.

Options:
    -c, --clean               If set, a clean build is created
    -b, --builddir=<path>     Sphinx build directory. If passed a relative
                              path, it will be interpreted as relative to
                              sourcedir [default: _build]
    -s, --suffix=<suffix>     Source file suffix [default: .rst]
    -t, --target=<file>       Name of file to launch in web browser (without
                              extension) [default: index]
    -i, --interface=<ip>      Interface to serve build on [default: 127.0.0.1]
    -p, --port=<port>         Port to serve build on [default: 16001]
    -n, --no-browser          Don't open a web browser pointed at target
"""

# TODO: List requirements
# TODO: Tests! But how?
# TODO: Python 2.7 anyone?

from docopt import docopt
from os import path, mkdir, chdir, stat
from time import sleep
from datetime import datetime
from urllib.parse import parse_qs
from re import search
from http.server import HTTPServer, SimpleHTTPRequestHandler
from subprocess import call
from shutil import rmtree
from socketserver import ThreadingMixIn
from threading import Thread
from shutil import copyfile
import webbrowser

__version__ = '0.1.0'


class Builder(object):
    sphinxview_output_dir = 'sphinxview'
    last_updated_fmt = 'html_last_updated_fmt=%% %Y%m%d%H%M%S %%'
    sphinxview_enabled_true = 'sphinxview_enabled=1'

    def __init__(self, source_dir, build_dir, suffix):
        self.source_dir = path.abspath(source_dir)
        self.build_dir = build_dir
        self.suffix = suffix
        self.output_dir = self.get_output_dir()

    def get_output_dir(self):
        if not path.isabs(self.build_dir):
            self.build_dir = path.join(self.source_dir, self.build_dir)
        output_dir = path.join(self.build_dir, Builder.sphinxview_output_dir)
        return output_dir

    def validate_dirs(self):
        if not path.isdir(self.source_dir):
            exit('Error: Source directory does not exist!')
        if not path.isdir(self.build_dir):
            exit('Error: Build directory does not exist!')

    def prepare_output_directory(self, clean):
        if clean:
            rmtree(self.build_dir)
            mkdir(self.build_dir)
        if not path.isdir(self.output_dir):
            mkdir(self.output_dir)

    def build(self):
        sphinx_call = ['sphinx-build']
        # set html builder
        sphinx_call.append('-b')
        sphinx_call.append('html')
        # force building all files
        sphinx_call.append('-a')
        # set last updated format
        sphinx_call.append('-D')
        sphinx_call.append(Builder.last_updated_fmt)
        # enable sphinxview extension
        sphinx_call.append('-D')
        sphinx_call.append(Builder.sphinxview_enabled_true)
        # set source and output directories
        sphinx_call.append(self.source_dir)
        sphinx_call.append(self.output_dir)

        call(sphinx_call)
        self.copy_javascript()

    def copy_javascript(self):
        here = path.abspath(path.dirname(__file__))
        js_source = path.join(here, 'sphinxview.js')
        static_dir = path.join(self.output_dir, '_static/')
        js_target = path.join(static_dir, 'sphinxview.js')
        if not path.isfile(js_target):
            copyfile(js_source, js_target)
            print('Copied sphinxview.js to', js_target)


class BuildHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP server with a SphinxBuilder used by the handler_class"""
    daemon_threads = True

    def __init__(self, server_address, builder):
        self.builder = builder
        handler_class = BuildRequestHandler
        super().__init__(server_address, handler_class)

    def serve_forever(self, poll_interval=0.5):
        chdir(self.builder.output_dir)
        print("===")
        print("Now serving on {0}".format(self.server_address))
        print("===")
        super().serve_forever(poll_interval)


class BuildRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.builder = server.builder
        super().__init__(request, client_address, server)

    def do_HEAD(self):
        if self.path.startswith('/polling?'):
            self.handle_polling()

    def handle_polling(self):
        query = parse_qs(self.path.partition('?')[-1])
        source_file = self.get_source_file(query)
        build_time = self.get_build_time(query)

        # while server.current_requested_url == my path
        while True:
            try:
                mtime = stat(source_file).st_mtime
                mtime = datetime.fromtimestamp(mtime)
            except OSError:
                # Sometimes when you save a file in a text editor it stops
                # existing for a brief moment.
                # See https://github.com/mgedmin/restview/issues/11
                sleep(0.1)
                continue

            if mtime > build_time:  # the file was modified after the build
                self.builder.build()
                self.send_response(200)
                self.send_header(
                    "Cache-Control", "no-cache, no-store, max-age=0")
                self.end_headers()
                return
            else:
                sleep(0.2)

    def get_source_file(self, query):
        # query['build_file'] returns a list, so take the first element
        relative_build_file = query['build_file'][0]
        # remove html extension and add rst extension
        relative_source_file = path.splitext(relative_build_file)[0] + \
            self.builder.suffix
        # remove leading / from relative_source_file to treat it as relative
        polled_source_file = path.join(
            self.builder.source_dir, relative_source_file[1:])
        return polled_source_file

    @staticmethod
    def get_build_time(query):
        last_updated = query['last_updated'][0]
        build_time = search(r'% (\d+) %', last_updated).group(1)
        build_time = datetime.strptime(build_time, '%Y%m%d%H%M%S')
        return build_time


def launch_browser(url):
    browser_thread = Thread(target=webbrowser.open, args=(url,))
    browser_thread.setDaemon(True)
    browser_thread.start()


def main():
    arguments = docopt(__doc__)

    # set up builder and do first build
    source_dir = arguments['<sourcedir>']
    build_dir = arguments['--builddir']
    suffix = arguments['--suffix']
    clean = arguments['--clean']

    builder = Builder(source_dir, build_dir, suffix)
    builder.validate_dirs()
    builder.prepare_output_directory(clean)
    builder.build()

    # set up server and launch browser
    interface = arguments['--interface']
    port = int(arguments['--port'])
    server_address = (interface, port)
    httpd = BuildHTTPServer(server_address, builder)

    browser = not arguments['--no-browser']
    if browser:
        target = arguments['--target']
        url_target = 'http://{0}:{1}/{2}.html'.format(interface, port, target)
        launch_browser(url_target)

    httpd.serve_forever()


if __name__ == '__main__':
    main()

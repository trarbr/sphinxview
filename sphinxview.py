#! /usr/bin/env python3

"""
sphinxview - serves your Sphinx project and reloads pages on source changes

Usage:
    sphinxview.py [options] <sourcedir>
    sphinxview.py -h | -- help

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

from docopt import docopt
from os import chdir, path
from time import sleep
from urllib.parse import parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler
from os import stat
from subprocess import call
from re import search
from shutil import rmtree
from socketserver import ThreadingMixIn
from threading import Thread
import webbrowser


# Hook into Sphinx extension API
def builder_inited(app):
    if app.config.sphinxview_enabled:
        app.add_javascript('sphinxview.js')


def setup(app):
    app.add_config_value('sphinxview_enabled', False, False)
    app.connect('builder-inited', builder_inited)

SPHINXVIEW_OUTPUT_DIR = 'sphinxview'
LAST_UPDATED_FMT = 'html_last_updated_fmt=%% %s %%'
SPHINXVIEW_ENABLED_TRUE = 'sphinxview_enabled=1'


class Builder(object):
    def __init__(self, source_dir, output_dir, suffix):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.suffix = suffix

        # validate source_dir

    def prepare_output_directory(self, clean):
        # handle output dir not exists
        if clean:
            rmtree(self.output_dir)

    def build_sphinx_project(self):
        sphinx_call = ['sphinx-build']
        # set html builder
        sphinx_call.append('-b')
        sphinx_call.append('html')
        # force building all files
        sphinx_call.append('-a')
        # set last updated format
        sphinx_call.append('-D')
        sphinx_call.append(LAST_UPDATED_FMT)
        # enable sphinxview extension
        sphinx_call.append('-D')
        sphinx_call.append(SPHINXVIEW_ENABLED_TRUE)
        # set source and output directories
        sphinx_call.append(self.source_dir)
        sphinx_call.append(self.output_dir)

        call(sphinx_call)


class BuildHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP server with a SphinxBuilder used by the handler_class"""
    daemon_threads = True

    def __init__(self, server_address, builder):
        self.builder = builder
        builder.build_sphinx_project()
        handler_class = BuildRequestHandler
        super().__init__(server_address, handler_class)

    def serve_forever(self, poll_interval=0.5):
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
                mtime = int(stat(source_file).st_mtime)
            except OSError:
                # Sometimes when you save a file in a text editor it stops
                # existing for a brief moment.
                # See https://github.com/mgedmin/restview/issues/11
                sleep(0.1)
                continue

            if mtime > build_time:  # the file was modified after the build
                self.builder.build_sphinx_project()
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
        build_time = int(search(r'% (\d+) %', last_updated).group(1))
        return build_time


def launch_browser(url):
    browser_thread = Thread(target=webbrowser.open, args=(url,))
    browser_thread.setDaemon(True)
    browser_thread.start()


def get_output_dir(source_dir, build_dir):
    if not path.isabs(build_dir):
        build_dir = path.join(source_dir, build_dir)
    output_dir = path.join(build_dir, SPHINXVIEW_OUTPUT_DIR)
    return output_dir


def main():
    arguments = docopt(__doc__)
    # set up builder and prepare output directory
    source_dir = arguments['<sourcedir>']
    source_dir = path.abspath(source_dir)
    build_dir = arguments['--builddir']
    output_dir = get_output_dir(source_dir, build_dir)
    suffix = arguments['--suffix']
    clean = arguments['--clean']

    builder = Builder(source_dir, output_dir, suffix)
    builder.prepare_output_directory(clean)

    # set up server and launch browser
    interface = arguments['--interface']
    port = int(arguments['--port'])
    server_address = (interface, port)
    browser = not arguments['--no-browser']

    if browser:
        target = arguments['--target']
        url_target = 'http://{0}:{1}/{2}.html'.format(interface, port, target)
        launch_browser(url_target)

    httpd = BuildHTTPServer(server_address, builder)
    chdir(output_dir)
    httpd.serve_forever()


if __name__ == '__main__':
    main()

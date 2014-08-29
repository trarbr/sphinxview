#! /usr/bin/env python3

"""
sphinxview-serve - like restview, but for Sphinx projects

Usage:
    sphinxview.py [options]
    sphinxview.py -h | -- help

Options:
    -c, --clean               If set, a clean build is created
    -s, --sourcedir=<path>    Directory containing the Sphinx source files
                              [default: .]
    -b, --builddir=<path>     Sphinx build directory. If passed a relative
                              path, it will be interpreted as relative to
                              sourcedir [default: _build]
    --suffix=<suffix>         Source file suffix [default: .rst]
    -t, --target=<file>       Name of file to launch in web browser (without
                              extension) [default: index]
    -i, --interface=<ip>      Interface to serve build on [default: 127.0.0.1]
    -p, --port=<port>         Port to serve build on [default: 16001]
    -n, --no-browser          Don't open a web browser pointed at target
"""

# TODO: Introduce seperate Builder class?
# TODO: List requirements
# TODO: Tests! But how?

from docopt import docopt
from os import chdir, path, getcwd
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

SPHINXVIEW_OUTPUT_DIR = 'sphinxview'
LAST_UPDATED_FMT = 'html_last_updated_fmt=%% %s %%'
SPHINXVIEW_ENABLED_TRUE = 'sphinxview_enabled=1'


class SphinxViewHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

    def __init__(
        self,
        server_address,
        handler_class,
        source_dir,
        output_dir,
        suffix,
    ):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.suffix = suffix
        self.build_sphinx_project()
        super().__init__(server_address, handler_class)

    def handle_request(self):
        print('handling a request')
        super().handle_request()

    def build_sphinx_project(self):
        sphinx_call = ['sphinx-build']
        # set builder
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

    def serve_forever(self, poll_interval=0.5):
        chdir(self.output_dir)
        print("===")
        print("Now serving on {0}".format(self.server_address))
        print("===")
        super().serve_forever(poll_interval)


class SphinxViewRequestHandler(SimpleHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def do_HEAD(self):
        print('Got HEAD request')
        if self.path.startswith('/polling?'):
            self.handle_polling()

    def get_polled_source_file(self, query):
        # query['build_file'] returns a list, so take the first element
        relative_build_file = query['build_file'][0]
        # remove html extension and add rst extension
        relative_source_file = path.splitext(relative_build_file)[0] + \
            self.server.suffix
        # remove leading / from relative_source_file to treat it as relative
        polled_source_file = path.join(
            self.server.source_dir, relative_source_file[1:])
        return polled_source_file

    def get_build_time(self, query):
        last_updated = query['last_updated'][0]
        build_time = int(search(r'% (\d+) %', last_updated).group(1))
        return build_time

    def handle_polling(self):
        print('I am being polled')
        print('Path: ', self.path)
        query = parse_qs(self.path.partition('?')[-1])
        source_file = self.get_polled_source_file(query)
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
                self.server.build_sphinx_project()
                self.send_response(200)
                self.send_header(
                    "Cache-Control", "no-cache, no-store, max-age=0")
                self.end_headers()
                return
            else:
                sleep(0.2)


def launch_browser(url):
    browser_thread = Thread(target=webbrowser.open, args=(url,))
    browser_thread.setDaemon(True)
    browser_thread.start()


# for debugging
def print_args(arguments):
    for key, value in arguments.items():
        print(key, value)
    exit()


def main():
    # parse arguments
    arguments = docopt(__doc__)
    #print_args(arguments)
    clean = arguments['--clean']
    source_dir = arguments['--sourcedir']
    if source_dir is not None:
        source_dir = path.abspath(source_dir)
    else:
        source_dir = getcwd()
    build_dir = arguments['--builddir']
    if not path.isabs(build_dir):
        build_dir = path.join(source_dir, build_dir)
    output_dir = path.join(build_dir, SPHINXVIEW_OUTPUT_DIR)
    target = arguments['--target'] + '.html'
    suffix = arguments['--suffix']
    interface = arguments['--interface']
    port = int(arguments['--port'])
    browser = not arguments['--no-browser']

    url_target = 'http://{0}:{1}/{2}'.format(interface, port, target)

    if clean:
        rmtree(output_dir)

    # set up server and launch browser
    server_address = (interface, port)
    handler_class = SphinxViewRequestHandler
    httpd = SphinxViewHTTPServer(
        server_address, handler_class, source_dir, output_dir, suffix)
    if browser:
        launch_browser(url_target)
    httpd.serve_forever()


if __name__ == '__main__':
    main()

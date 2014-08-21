Things I learned while writing sphinxview
=========================================

In Python, when inheriting from multiple classes, the order of those classes
matter. For example, we want to make a threaded HTTP server - the standard HTTP
server from ``http.server`` in the standard library is single-threaded. Luckily,
all we need to do is make a new class that inherits from both ``HTTPServer`` and
``ThreadedMixIn`` (from the ``socketserver`` module). But the ordering matters,
e.g::

   class ThreadedHTTPServer(HTTPServer, ThreadingMixIn):
       pass

is not equal to::

   class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
       pass

In fact, one of them is going to be single-threaded while the other one will be
multi-threaded. But which one, and why?

The correct example is the second one: ``ThreadingMixIn`` has to come first.
The reason is that ``ThreadingMixIn`` overrides a method in ``HTTPServer``
called ``process_request`` (which ``HTTPServer`` inherits from ``TCPServer``).

Why this matters come down to the question of Method Resolution Order (MRO).
Should ``process_request`` be called on ``ThreadingMixIn`` or ``HTTPServer``,
when it is called on ``ThreadedHTTPServer``?

Python 3 uses the C3 algorithm to answer this question. You can read more about
that in the `Python History`_ article about it.

.. _Python History: http://python-history.blogspot.dk/2010/06/method-resolution-order.html

In this simple example, it's going to be the first class that
``ThreadedHTTPServer`` inherits from. And that's why ``ThreadingMixIn`` has to
be first!

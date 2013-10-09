.. _wsgisubdomain:

.. toctree::
   :maxdepth: 2

*************
wsgisubdomain
*************

.. module:: wsgisubdomain

wsgisubdomain is a WSGI application dispatcher. A WSGI application is fetched
based on a request's target subdomain, creating one if needed.

wsgisubdomain supports Python 2.6, 2.7, 3.2, 3.3 and PyPy.

The code in this module is adapted from:
 http://flask.pocoo.org/docs/patterns/appdispatch/#dispatch-by-subdomain

.. _usecase:
    In Flask, one way to have your site available as both example.com and
    www.example.com is to have two separate application instances with the
    SERVER_NAME configured for each.

.. _wsgisubdomain_source: https://github.com/xsleonard/pystmark

.. _installation:

Installation
============

    $ pip install wsgisubdomain

.. _example:

Example
=======

.. code-block:: python

    # app.wsgi
    from wsgisubdomain import SubdomainDispatcher
    from app import create_application
    application = SubdomainDispatcher(create_application)

.. _api:

API
===

.. _subdomain_dispatcher:

Subdomain Dispatcher
====================

.. autoclass:: wsgisubdomain.SubdomainDispatcher
    :special-members: __call__
    :inherited-members:

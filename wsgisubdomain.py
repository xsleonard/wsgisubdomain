import socket
from threading import Lock
from __about__ import __version__, __title__, __description__

__all__ = ['__version__', '__title__', '__description__',
           'SubdomainDispatcher']


class SubdomainDispatcher(object):

    """ A WSGI application that gets or creates other WSGI applications
    based on the subdomain.

    Adapted from:
    http://flask.pocoo.org/docs/patterns/appdispatch/#dispatch-by-subdomain

    :param create_application: A function that accepts 'subdomain' as a
        keyword argument and returns a WSGI application.  Subdomain will be
        either an empty string for the bare domain, `None` if the request is
        for an IP address, or a full subdomain (e.g. 'www' or 'en.dl')
    """

    def __init__(self, create_application):
        self.create_application = create_application
        self.lock = Lock()
        self.instances = {}

    def __call__(self, environ, start_response):
        """ WSGI application interface

        :param environ: WSGI environ
        :param start_response: WSGI start_response
        """
        app = self.get_application(environ)
        return app(environ, start_response)

    def get_application(self, environ):
        """ Retrieve an application for a wsgi environ

        :param environ: The environ object sent by wsgi to an application
        """
        host = self._get_host(environ)
        subdomain = self._extract_subdomain(host)
        return self._get_application(subdomain)

    def _get_application(self, subdomain):
        """ Return a WSGI application for subdomain.  The subdomain is
        passed to the create_application constructor as a keyword argument.

        :param subdomain: Subdomain to get or create an application with
        """
        with self.lock:
            app = self.instances.get(subdomain)
            if app is None:
                app = self.create_application(subdomain=subdomain)
                self.instances[subdomain] = app
            return app

    @staticmethod
    def _extract_subdomain(host):
        """ Returns a subdomain from a host. This host is typically the
        HTTP_HOST request envvar.  If the host is an IP address, `None` is
        returned

        :param host: Request's target host
        """
        host = host.split(':')[0]
        # If the host is an IP address, there is no subdomain to extract
        try:
            # Check if the host is an ip address
            socket.inet_aton(host)
        except socket.error:
            # It isn't an IP address, return the subdomain
            return '.'.join(host.split('.')[:-2])

    @staticmethod
    def _get_host(environ):
        """ Returns the true host from the request's environ.

        :param environ: environ variable passed to a wsgi app by wsgi
        """
        # HTTP_HOST is preferred to SERVER_NAME, but only SERVER_NAME is
        # guaranteed to exist
        return environ.get('HTTP_HOST', environ['SERVER_NAME'])

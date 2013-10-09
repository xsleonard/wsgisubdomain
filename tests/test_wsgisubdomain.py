from unittest import TestCase
from wsgisubdomain import SubdomainDispatcher


class TestSubdomainDispatcher(TestCase):

    def assertIs(self, a, b):
        try:
            super(TestSubdomainDispatcher, self).assertIs(a, b)
        except AttributeError:
            # python 2.6 support
            self.assertTrue(a is b)

    @staticmethod
    def create_app(subdomain=None):
        return lambda x, y: subdomain

    def test_create(self):
        s = SubdomainDispatcher(1)
        self.assertEqual(s.create_application, 1)
        self.assertTrue(hasattr(s, 'lock'))
        self.assertFalse(s.instances)

    def test_get_host(self):
        environ = dict(HTTP_HOST='xxx.example.com', SERVER_NAME='example.com')
        self.assertEqual('xxx.example.com',
                         SubdomainDispatcher._get_host(environ))
        del environ['HTTP_HOST']
        self.assertEqual('example.com', SubdomainDispatcher._get_host(environ))

    def test_extract_subdomain(self):
        # Test with ip address, returns None
        s = SubdomainDispatcher
        h = '127.0.0.1'
        self.assertIs(s._extract_subdomain(h), None)
        self.assertIs(s._extract_subdomain(h + ':888'), None)
        # Test with no subdomain
        h = 'example.com'
        self.assertEqual(s._extract_subdomain(h), '')
        self.assertEqual(s._extract_subdomain(h + ':888'), '')
        # Test with a single subdomain
        h = 'www.example.com'
        self.assertEqual(s._extract_subdomain(h), 'www')
        self.assertEqual(s._extract_subdomain(h + ':888'), 'www')
        # Test with multiple subdomains
        h = 'a.b.c.d.example.com'
        self.assertEqual(s._extract_subdomain(h), 'a.b.c.d')
        self.assertEqual(s._extract_subdomain(h + ':888'), 'a.b.c.d')

    def test_get_application(self):
        s = SubdomainDispatcher(self.create_app)
        environ = dict(HTTP_HOST='xxx.example.com', SERVER_NAME='example.com')
        app = s.get_application(environ)
        self.assertEqual(app(0, 0), 'xxx')
        environ['HTTP_HOST'] = 'example.com'
        app = s.get_application(environ)
        self.assertEqual(app(0, 0), '')
        environ['HTTP_HOST'] = '127.0.0.1'
        app = s.get_application(environ)
        self.assertIs(app(0, 0), None)

    def test_call(self):
        s = SubdomainDispatcher(self.create_app)
        environ = dict(HTTP_HOST='xxx.example.com', SERVER_NAME='example.com')
        app = s(environ, None)
        self.assertEqual(app, 'xxx')
        environ['HTTP_HOST'] = 'example.com'
        app = s(environ, None)
        self.assertEqual(app, '')
        environ['HTTP_HOST'] = '127.0.0.1'
        app = s(environ, None)
        self.assertIs(app, None)

#!/usr/bin/env python

from __future__ import print_function
import subprocess
import shlex
import os
import sys
from setuptools import setup, Command

pypy = False
if 'pypy' in sys.version.lower():
    pypy = True


about = {}
with open('__about__.py') as f:
    exec(f.read(), about)


class Test(Command):
    ''' Test application with the following:
        pep8 conformance (style)
        pyflakes validation (static analysis)
        no print statements (breaks wsgi)
        nosetests (code tests) [--with-integration] [--run-failed]
    '''
    description = 'Test {0} source code'.format(about['__title__'])
    user_options = [('run-failed', None,
                     'Run only the previously failed tests.'),
                    ('nose-only', None, 'Run only the nose tests.')]
    boolean_options = ['run-failed', 'nose-only']

    _files = ['__about__.py', 'wsgisubdomain.py']

    _test_requirements = ['nose', 'disabledoc', 'coverage']

    @property
    def files(self):
        return ' '.join(self._files)

    def initialize_options(self):
        self.run_failed = False
        # Disable the flake8 tests in pypy due to bug in pep8 module
        self.nose_only = pypy
        self.with_integration = False
        self.flake8 = 'flake8 {0} tests/'.format(self.files)

    def finalize_options(self):
        pass

    def _no_print_statements(self):
        cmd = 'grep -rnw print {0}'.format(self.files)
        p = subprocess.Popen(shlex.split(cmd), close_fds=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        err = p.stderr.read().strip()
        if err:
            msg = 'ERROR: stderr not empty for print statement grep: {0}'
            print(msg.format(err))
            raise SystemExit(-1)
        output = p.stdout.read().strip()
        if output:
            print('ERROR: Found print statements in source code:')
            print(output)
            raise SystemExit(-1)

    def _get_py_files(self, basepath, subpath=''):
        files = []
        badchars = ['.', '_', '~']
        path = os.path.join(basepath, subpath)
        for f in os.listdir(path):
            if (not f.endswith('.py') or
                    any(map(lambda c: f.startswith(c), badchars))):
                continue
            files.append(os.path.join(subpath, f))
        return files

    def _get_nose_command(self):
        nosecmd = ('nosetests -v -w tests/ --all-modules '
                   '--with-coverage --disable-docstring')
        if self.run_failed:
            nosecmd += ' --failed'
        nose = ' '.join(shlex.split(nosecmd))
        return nose

    def _check_module(self, module):
        cmd = '/usr/bin/env python -c "import {0}"'.format(module)
        try:
            subprocess.check_call(shlex.split(cmd))
        except subprocess.CalledProcessError:
            msg = 'Python package "{0}" is required to run the tests'
            print(msg.format(module))
            raise SystemExit(-1)

    def _check_test_packages(self):
        for m in self._test_requirements:
            self._check_module(m)

    def _remove_coverage(self):
        fn = '.coverage'
        if os.path.exists(fn):
            os.remove(fn)

    def run(self):
        self._check_test_packages()
        cmds = [self._get_nose_command()]
        if not self.nose_only:
            self._no_print_statements()
            self._remove_coverage()
            cmds = [self.flake8] + cmds
        cmds = filter(bool, cmds)
        if not cmds:
            print('No action taken.')
            SystemExit(-2)
        try:
            list(map(subprocess.check_call, map(shlex.split, cmds)))
        except subprocess.CalledProcessError:
            raise SystemExit(-1)
        raise SystemExit(0)


setup(name=about['__title__'],
      version=about['__version__'],
      description=about['__description__'],
      long_description=open('README.md').read(),
      author='Steve Leonard',
      author_email='sleonard76@gmail.com',
      url='https://github.com/xsleonard/wsgisubdomain',
      platforms='any',
      py_modules=['__about__', 'wsgisubdomain'],
      install_requires=[],
      cmdclass=dict(test=Test),
      license='MIT',
      keywords='wsgi subdomain',
      classifiers=(
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: MIT License',
      ))

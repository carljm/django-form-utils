from setuptools import setup
import subprocess
import os.path

try:
    # don't get confused if our sdist is unzipped in a subdir of some
    # other hg repo
    if os.path.isdir('.hg'):
        p = subprocess.Popen(['hg', 'parents', r'--template={rev}\n'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not p.returncode:
            fh = open('HGREV', 'w')
            fh.write(str(p.communicate()[0].splitlines()[0]))
            fh.close()
except (OSError, IndexError):
    pass

try:
    hgrev = open('HGREV').read()
except IOError:
    hgrev = ''

long_description = open('README.rst').read() + '\n\n' + open('CHANGES.rst').read()

setup(
    name='django-form-utils',
    version='1.0.3.post%s' % hgrev,
    description='Form utilities for Django',
    long_description=long_description,
    author='Carl Meyer',
    author_email='carl@oddbird.net',
    url='http://bitbucket.org/carljm/django-form-utils/',
    packages=['form_utils', 'form_utils.templatetags'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Framework :: Django',
    ],
    zip_safe=False,
    package_data={'form_utils': ['templates/form_utils/*.html',
                                 'media/form_utils/js/*.js']},
    test_suite='tests.runtests.runtests',
    tests_require=['Django', 'mock', 'Pillow'],
)

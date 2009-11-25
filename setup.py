from setuptools import setup

long_description = open('README.txt').read() + open('CHANGES.txt').read()

setup(
    name='django-form-utils',
    version='0.1.5.post',
    description='Form utilities for Django',
    long_description=long_description,
    author='Carl Meyer',
    author_email='carl@dirtcircle.com',
    url='http://bitbucket.org/carljm/django-form-utils/',
    packages=['form_utils', 'form_utils.templatetags'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe=False,
    package_data={'form_utils': ['templates/form_utils/*.html']},
    test_suite='tests.runtests.runtests'
)

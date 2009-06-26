from setuptools import setup, find_packages
 
setup(
    name='django-form-utils',
    version='0.1.1',
    description='Form utilities for Django',
    long_description=open('README.txt').read(),
    author='Carl Meyer',
    author_email='carl@dirtcircle.com',
    url='http://launchpad.net/django-form-utils',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    setup_requires=['setuptools_bzr'],
)

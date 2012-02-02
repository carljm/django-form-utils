#!/usr/bin/env python

import os, sys

from django.conf import settings


if not settings.configured:
    settings_dict = dict(
        INSTALLED_APPS=['form_utils', 'tests'],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                }
            },
        MEDIA_ROOT=os.path.join(os.path.dirname(__file__), 'media'),
        MEDIA_URL='/media/',
        )

    settings.configure(**settings_dict)


def runtests(*test_args):
    if not test_args:
        test_args = ['tests']

    parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent)

    from django.test.simple import DjangoTestSuiteRunner
    failures = DjangoTestSuiteRunner(
        verbosity=1, interactive=True, failfast=False).run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()

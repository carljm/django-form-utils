#!/usr/bin/env python

import os, sys

parent = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))

sys.path.insert(0, parent)

from django.core.management import setup_environ, call_command
import test_settings
setup_environ(test_settings)
call_command('test', 'form_utils')

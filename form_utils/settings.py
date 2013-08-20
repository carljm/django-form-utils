# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import posixpath

from django.conf import settings

JQUERY_URL = getattr(
    settings, 'JQUERY_URL',
    'http://ajax.googleapis.com/ajax/libs/jquery/1.8/jquery.min.js')

if not ((':' in JQUERY_URL) or (JQUERY_URL.startswith('/'))):
    JQUERY_URL = posixpath.join(settings.STATIC_URL, JQUERY_URL)

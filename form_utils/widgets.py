"""
widgets for django-form-utils

Time-stamp: <2008-11-22 17:32:48 carljm widgets.py>

parts of this code taken from http://www.djangosnippets.org/snippets/934/
 - thanks baumer1122

"""
import os

from PIL import Image

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

try:
    from sorl.thumbnail.main import DjangoThumbnail
    def thumbnail(image_path):
        t = DjangoThumbnail(relative_source=image_path, requested_size=(200,200))
        return u'<img src="%s" alt="%s" />' % (t.absolute_url, image_path)
except ImportError:
    def thumbnail(image_path):
        absolute_url = os.path.join(settings.MEDIA_ROOT, image_path)
        return u'<img src="%s" alt="%s" />' % (absolute_url, image_path)

class ImageWidget(forms.widgets.FileInput):
    def render(self, name, value, attrs=None):
        file_name = str(value)
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        output = []
        output.append(super(forms.widgets.FileInput, self).render(name, value, attrs))
        try: # is image
            Image.open(file_path)
            output.append('<br />%s' % (thumbnail(str(value)),))
        except IOError: # not image
            pass
        return mark_safe(u''.join(output))

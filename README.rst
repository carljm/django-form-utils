=================
django-form-utils
=================

This application provides utilities for enhancing Django's form handling:

    1. ``BetterForm`` and ``BetterModelForm`` classes, which are
       subclasses of ``django.forms.Form`` and
       ``django.forms.ModelForm``, respectively.  ``BetterForm`` and
       ``BetterModelForm`` allow subdivision of forms into fieldsets
       which are iterable from a template, and also allow definition
       of ``row_attrs`` which can be accessed from the template to
       apply attributes to the surrounding container (<li>, <tr>, or
       whatever) of a specific form field.
    
    2. A ``ClearableFileField`` to enhance ``FileField`` and
       ``ImageField`` with a checkbox for clearing the contents of the
       field.

    3. An ``ImageWidget`` which display a thumbnail of the image
       rather than just the filename.

    4. An ``AutoResizeTextarea`` widget which auto-resizes to
       accomodate its contents.

Installation
============

Install from PyPI with ``easy_install`` or ``pip``::

    pip install django-form-utils

or get the `in-development version`_::

    pip install django-form-utils==dev

.. _in-development version: http://bitbucket.org/carljm/django-form-utils/get/tip.gz#egg=django_form_utils-dev

To use ``django-form-utils`` in your Django project, just include
``form_utils`` in your INSTALLED_APPS setting.  ``django-form-utils`` does
not provide any models, but including it in INSTALLED_APPS makes the
``form_utils`` template tag library available.

You may also want to override the default form rendering templates by
providing alternate templates at ``templates/form_utils/better_form.html``
and ``templates/form_utils/form.html``.

Dependencies
------------

``django-form-utils`` requires `Django`_ 1.0 or later.

`ClearableFileField`_ requires `Django`_ 1.1 or later. 

`ImageWidget`_ requires the `Python Imaging Library`_.
`sorl-thumbnail`_ is optional, but without it full-size images will be
displayed instead of thumbnails.

`AutoResizeTextarea`_ requires `jQuery`_ (by default using a
Google-served version; see `JQUERY_URL`_).

.. _Django: http://www.djangoproject.com/
.. _sorl-thumbnail: http://pypi.python.org/pypi/sorl-thumbnail
.. _Python Imaging Library: http://www.pythonware.com/products/pil/
.. _jQuery: http://www.jquery.com/

Usage
=====

BetterForm
----------

Simply inherit your form class from ``form_utils.forms.BetterForm`` (rather
than ``django.forms.Form``), or your modelform class from
``form_utils.forms.BetterModelForm``, and define the ``fieldsets`` and/or
``row_attrs`` attributes of the inner Meta class::

    class MyForm(BetterForm):
        one = forms.CharField()
        two = forms.CharField()
        three = forms.CharField()
        class Meta:
            fieldsets = (('main', {'fields': ('two',), 'legend': ''}),
                         ('Advanced', {'fields': ('three', 'one'),
                                       'description': 'advanced stuff',
                                       'classes': ('advanced', 'collapse'}))
            row_attrs = {'one': {'style': 'display: none'}}

fieldsets
'''''''''

Fieldset definitions are similar to ModelAdmin fieldset definitions:
each fieldset is a two-tuple with a name and an options
dictionary. Valid fieldset options in the dictionary include:

``fields``
  (required) A tuple of field names to display in this fieldset.

``classes``
  A tuple/list of extra CSS classes to apply to the fieldset.

``legend``
  This value, if present, will be the contents of a ``legend``
  tag to open the fieldset.  If not present the name of the fieldset will
  be used (so a value of '' for legend must be used if no legend is
  desired.)

``description``
  A string of optional extra text to be displayed
  under the ``legend`` of the fieldset.

When iterated over, the ``fieldsets`` attribute of a ``BetterForm``
(or ``BetterModelForm``) yields ``Fieldset`` s.  Each ``Fieldset`` has
a ``name`` attribute, a ``legend`` attribute, a ``classes`` attribute
(the ``classes`` tuple collapsed into a space-separated string), and a
``description`` attribute, and when iterated over yields its
``BoundField`` s.

For backwards compatibility, a ``BetterForm`` or ``BetterModelForm`` can
still be iterated over directly to yield all of its ``BoundField`` s,
regardless of fieldsets.

For more detailed examples, see the tests in ``tests/tests.py``.

row_attrs
'''''''''

The row_attrs declaration is a dictionary mapping field names to
dictionaries of attribute/value pairs.  The attribute/value
dictionaries will be flattened into HTML-style attribute/values
(i.e. {'style': 'display: none'} will become ``style="display:
none"``), and will be available as the ``row_attrs`` attribute of the
``BoundField``.

Also, a CSS class of "required" or "optional" will automatically be
added to the row_attrs of each ``BoundField``, depending on whether
the field is required.

Rendering
'''''''''

A possible template for rendering a ``BetterForm``::

    {% if form.non_field_errors %}{{ form.non_field_errors }}{% endif %}
    {% for fieldset in form.fieldsets %}
      <fieldset class="{{ fieldset.classes }}">
      {% if fieldset.legend %}
        <legend>{{ fieldset.legend }}</legend>
      {% endif %}
      {% if fieldset.description %}
        <p class="description">{{ fieldset.description }}</p>
      {% endif %}
      <ul>
      {% for field in fieldset %}
        {% if field.is_hidden %}
          {{ field }}
        {% else %}
          <li{{ field.row_attrs }}>
            {{ field.errors }}
            {{ field.label_tag }}
            {{ field }}
          </li>
        {% endif %}
      {% endfor %}
      </ul>
      </fieldset>
    {% endfor %}


``django-form-utils`` also provides a convenience template filter,
``render``.  It is used like this::

    {{ form|render }}

By default, it will check whether the form is a ``BetterForm``, and if
so render it using the template ``form_utils/better_form.html``.  If
not, it will render it using the template ``form_utils/form.html``.
(In either case, the form object will be passed to the render
template's context as ``form``).

The render filter also accepts an optional argument, which is a
template name or comma-separated list of template names to use for
rendering the form::

    {{ form|render:"my_form_stuff/custom_form_template.html" }}

ClearableFileField
------------------

A replacement for ``django.forms.FileField`` that has a checkbox to
clear the field of an existing file. Use as you would any other form
field class::

    from django import forms

    from form_utils.fields import ClearableFileField

    class MyModelForm(forms.ModelForm):
        pdf = ClearableFileField()

``ClearableFileField`` also accepts two keyword arguments,
``file_field`` and ``template``.

``file_field`` is the instantiated field to actually use for
representing the file portion. For instance, if you want to use
``ClearableFileField`` to replace an ``ImageField``, and you want to
use `ImageWidget`_, you could do the following::

    from django import forms

    from form_utils.fields import ClearableFileField
    from form_utils.widgets import ImageWidget

    class MyModelForm(forms.ModelForm):
        avatar = ClearableFileField(
            file_field=forms.ImageField(widget=ImageWidget))

By default, ``file_field`` is a plain ``forms.FileField`` with the
default ``forms.FileInput`` widget.

``template`` is a string defining how the ``FileField`` (or
alternative ``file_field``) and the clear checkbox are displayed in
relation to each other. The template string should contain variable
interpolation markers ``%(input)s`` and ``%(checkbox)s``. The default
value is ``%(input)s Clear: %(checkbox)s``.

To use ``ClearableFileField`` in the admin; just inherit your admin
options class from ``form_utils.admin.ClearableFileFieldsAdmin``
instead of ``django.contrib.admin.ModelAdmin``, and all ``FileField``s
and ``ImageField``s in that model will automatically be made clearable
(while still using the same file/image field/widget they would have
otherwise, including any overrides you provide in
``formfield_overrides``).

ClearableImageField
-------------------

``form_utils.fields.ClearableImageField`` is just a
``ClearableFileField`` with the default file field set to
``forms.ImageField`` rather than ``forms.FileField``.

ImageWidget
-----------

A widget for representing an ``ImageField`` that includes a thumbnail
of the current image in the field, not just the name of the
file. (Thumbnails only available if `sorl-thumbnail`_ is installed;
otherwise the full-size image is displayed). To use, just pass in as
the widget class for an ``ImageField``::

    from django import forms
     
    from form_utils.widgets import ImageWidget
    
    class MyForm(forms.Form):
        pic = forms.ImageField(widget=ImageWidget())

``ImageWidget`` accepts a keyword argument, ``template``. This is a
string defining how the image thumbnail and the file input widget are
rendered relative to each other. The template string should contain
variable interpolation markers ``%(input)s`` and ``%(image)s``. The
default value is ``%(input)s<br />%(image)s``. For example, to display
the image above the input rather than below::

    pic = forms.ImageField(
        widget=ImageWidget(template='%(image)s<br />%(input)s'))

To use in the admin, set as the default widget for ``ImageField``
using ``formfield_overrides``::

    from django.db import models

    from form_utils.widgets import ImageWidget

    class MyModelAdmin(admin.ModelAdmin):
        formfield_overrides = { models.ImageField: {'widget': ImageWidget}}

.. _sorl-thumbnail: http://pypi.python.org/pypi/sorl-thumbnail

AutoResizeTextarea
------------------

Just import the widget and assign it to a form field::

    from django import forms
    from form_utils.widgets import AutoResizeTextarea
    
    class MyForm(forms.Form):
        description = forms.CharField(widget=AutoResizeTextarea())

Or use it in ``formfield_overrides`` in your ``ModelAdmin`` subclass::

    from django import forms
    from django.contrib import admin
    from form_utils.widgets import AutoResizeTextarea
    
    class MyModelAdmin(admin.ModelAdmin):
        formfield_overrides = {forms.CharField: {'widget': AutoResizeTextarea()}}

There is also an ``InlineAutoResizeTextarea``, which simply provides
smaller default sizes suitable for use in a tabular inline.

Settings
========

FORM_UTILS_MEDIA_URL
--------------------

Some projects separate user-uploaded media at ``MEDIA_URL`` from
static assets. If you keep static assets at a URL other than
``MEDIA_URL``, just set ``FORM_UTILS_MEDIA_URL`` to that URL, and make
sure the contents of the ``form_utils/media/form_utils`` directory are
available at ``FORM_UTILS_MEDIA_URL/form_utils/``.


JQUERY_URL
----------

`AutoResizeTextarea`_ requires the jQuery Javascript library.  By
default, ``django-form-utils`` links to the most recent minor version
of jQuery 1.4 available at ajax.googleapis.com (via the URL
``http://ajax.googleapis.com/ajax/libs/jquery/1.3/jquery.min.js``).
If you wish to use a different version of jQuery, or host it yourself,
set the JQUERY_URL setting.  For example::

    JQUERY_URL = 'jquery.min.js'

This will use the jQuery available at MEDIA_URL/jquery.min.js. Note
that a relative ``JQUERY_URL`` is always relative to ``MEDIA_URL``, it
does not use ``FORM_UTILS_MEDIA_URL``.


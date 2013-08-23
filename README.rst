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

    2. A variety of small template filters that are useful for giving template
       authors more control over custom rendering of forms without needing to
       edit Python code: `label`_, `value_text`_, `selected_values`_,
       `optional`_, `is_checkbox`_, and `is_multiple`_.

    2. A ``ClearableFileField`` to enhance ``FileField`` and
       ``ImageField`` with a checkbox for clearing the contents of the
       field.

    3. An ``ImageWidget`` which display a thumbnail of the image
       rather than just the filename.

    4. An ``AutoResizeTextarea`` widget which auto-resizes to
       accommodate its contents.


Installation
============

Install from PyPI with ``easy_install`` or ``pip``::

    pip install django-form-utils

To use ``django-form-utils`` in your Django project, just include
``form_utils`` in your INSTALLED_APPS setting.  ``django-form-utils`` does
not provide any models, but including it in INSTALLED_APPS makes the
``form_utils`` template tag library available.

You may also want to override the default form rendering templates by
providing alternate templates at ``templates/form_utils/better_form.html``
and ``templates/form_utils/form.html``.

Dependencies
------------

``django-form-utils`` is tested on `Django`_ 1.4 and later and `Python`_ 2.6,
2.7, and 3.3. It is known to be incompatible with Python 3.0, 3.1, and 3.2.

`ImageWidget`_ requires the `Python Imaging Library`_.
`sorl-thumbnail`_ or `easy-thumbnails`_ is optional, but without it
full-size images will be displayed instead of thumbnails. The default
thumbnail size is 200px x 200px.

`AutoResizeTextarea`_ requires `jQuery`_ (by default using a
Google-served version; see `JQUERY_URL`_).

.. _Django: http://www.djangoproject.com/
.. _Python: http://www.python.org/
.. _sorl-thumbnail: http://pypi.python.org/pypi/sorl-thumbnail
.. _easy-thumbnails: http://pypi.python.org/pypi/easy-thumbnails
.. _Python Imaging Library: http://python-imaging.github.io/
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
            fieldsets = [('main', {'fields': ['two'], 'legend': ''}),
                         ('Advanced', {'fields': ['three', 'one'],
                                       'description': 'advanced stuff',
                                       'classes': ['advanced', 'collapse']})]
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

If you set ``fieldsets`` on a ``BetterModelForm`` and don't set either
the ``fields`` or ``exclude`` options on that form class,
``BetterModelForm`` will set ``fields`` to be the list of all fields
present in your ``fieldsets`` definition. This avoids problems with
forms that can't validate because not all fields are listed in a
``fieldset``. If you manually set either ``fields`` or ``exclude``,
``BetterModelForm`` assumes you know what you're doing and doesn't
touch those definitions, even if they don't match the fields listed in
your fieldsets.

For more detailed examples, see the tests in ``tests/tests.py``.

row_attrs
'''''''''

The row_attrs declaration is a dictionary mapping field names to
dictionaries of attribute/value pairs.  The attribute/value
dictionaries will be flattened into HTML-style attribute/values
(i.e. {'style': 'display: none'} will become ``style="display:
none"``), and will be available as the ``row_attrs`` attribute of the
``BoundField``.

A ``BetterForm`` or ``BetterModelForm`` will add a CSS class of
"required" or "optional" automatically to the row_attrs of each
``BoundField`` depending on whether the field is required, and will
also add a CSS class of "error" if the field has errors.

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


One can also access the fieldset directly if any special casing needs to be
done, e.g.::

    {% for field in form.fieldsets.main %}
        ...
    {% endfor %}

``django-form-utils`` also provides a convenience template filter,
``render``.  It is used like this::

    {% load form_utils %}

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


Utility Filters
---------------

All the below filters require ``{% load form_utils %}`` in the template where
they are used.

These filters are complementary to the useful filters found in the
`django-widget-tweaks`_ library for setting arbitrary attributes and classes on
form field widgets; thus such filters are not provided in
``django-form-utils``.

.. _django-widget-tweaks: http://pypi.python.org/pypi/django-widget-tweaks


label
'''''

Render a label tag for the given form field by rendering the template
``forms/_label.html`` with the context ``field`` (the boundfield object),
``id`` (the form field id attribute), and ``label_text``.

By default the Python-defined label text for the form field is used, but
alternate label text can be provided as an argument to the filter::

    {{ form.fieldname|label:"Alternate label" }}


value_text
''''''''''

Display the current value of the given form field in a human-readable way
(i.e. display labels for choice values rather than the internal value). The
current value may be the default value (for first-time rendering of a form) or
the previously-input value (for repeat rendering of a form with
errors). Usage::

    {{ form.fieldname|value_text }}


selected_values
'''''''''''''''

Similar to `value_text`_, but for use with multiple-select form fields, and
returns a list of selected values rather than a single string. Usage::

    <ul>
      {% for selected_value in form.multiselect|selected_values %}
        <li>{{ selected_value }}</li>
      {% endfor %}
    </ul>


optional
''''''''

Return ``True`` if the given field is optional, ``False`` if it is
required. Sample usage::

    {% if form.fieldname|optional %}(optional){% endif %}


is_checkbox
'''''''''''

Return ``True`` if the given field's widget is a ``CheckboxInput``, ``False``
otherwise. Sample usage::

    {% if form.fieldname|is_checkbox %}
      {{ form.fieldname }}
      {{ form.fieldname|label }}
    {% else %}
      {{ form.fieldname|label }}
      {{ form.fieldname }}
    {% endif %}


is_multiple
'''''''''''

Return ``True`` if the given field is a ``MultipleChoiceField``, ``False``
otherwise. Sample usage::

    {% if form.fieldname|is_multiple %}
      {% for value in form.fieldname|selected_values %}{{ value }} {% endif %}
    {% else %}
      {{ form.fieldname|value_text }}
    {% endif %}



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


JQUERY_URL
----------

`AutoResizeTextarea`_ requires the jQuery Javascript library.  By
default, ``django-form-utils`` links to the most recent minor version
of jQuery 1.8 available at ajax.googleapis.com (via the URL
``http://ajax.googleapis.com/ajax/libs/jquery/1.8/jquery.min.js``).
If you wish to use a different version of jQuery, or host it yourself,
set the JQUERY_URL setting.  For example::

    JQUERY_URL = 'jquery.min.js'

This will use the jQuery available at STATIC_URL/jquery.min.js. Note
that a relative ``JQUERY_URL`` is relative to ``STATIC_URL``.

=================
django-form-utils
=================

This application provides BetterForm and BetterModelForm classes which are
subclasses of django.forms.Form and django.forms.ModelForm, respectively.
BetterForm and BetterModelForm allow subdivision of forms into fieldsets
which are iterable from a template, and also allow definition of row_attrs
which can be accessed from the template to apply attributes to the
surrounding container (<li>, <tr>, or whatever) of a specific form field.

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

Usage
=====

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

For more detailed examples, see the doctests in tests/__init__.py.

Rendering
---------

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


``django-form-utils`` also provides a convenience template filter, ``render``.  It is used like this::

    {{ form|render }}

By default, it will check whether the form is a ``BetterForm``, and if so render it using the template ``form_utils/better_form.html``.  If not, it will render it using the template ``form_utils/form.html``.  (In either case, the form object will be passed to the render template's context as ``form``).

The render filter also accepts an optional argument, which is a template name or comma-separated list of template names to use for rendering the form::

    {{ form|render:"my_form_stuff/custom_form_template.html" }}


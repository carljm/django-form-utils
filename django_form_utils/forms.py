"""
forms for django_form_utils

Time-stamp: <2008-10-13 12:08:30 carljm forms.py>

"""
from copy import deepcopy

from django import forms
from django.forms.util import flatatt
from django.utils.safestring import mark_safe

class Fieldset(object):
    """
    An iterable Fieldset with a legend and a set of BoundFields.

    """
    def __init__(self, form, name, boundfields, legend=None, description=''):
        self.form = form
        self.boundfields = boundfields
        if legend is None: legend = name
        self.legend = legend
        self.description = description
        self.name = name

    def __iter__(self):
        for bf in self.boundfields:
            yield _mark_row_attrs(bf, self.form)

    def __repr__(self):
        return "%s('%s', %s, legend='%s', description='%s')" % (
            self.__class__.__name__, self.name,
            [f.name for f in self.boundfields], self.legend, self.description)

class FieldsetCollection(object):
    def __init__(self, form, fieldsets):
        self.form = form
        self.fieldsets = fieldsets

    def __iter__(self):
        if not self.fieldsets:
            self.fieldsets = (('main', {'fields': self.form.fields.keys(),
                                        'legend': ''}),)
        for name, options in self.fieldsets:
            try:
                field_names = [n for n in options['fields']
                               if n in self.form.fields]
            except KeyError:
                raise ValueError("Fieldset definition must include 'fields' option." )
            boundfields = [forms.forms.BoundField(self.form, self.form.fields[n], n)
                           for n in field_names]
            yield Fieldset(self.form, name, boundfields,
                           options.get('legend', None),
                           options.get('description', ''))

def _get_meta_attr(attrs, attr, default):
    try:
        ret = getattr(attrs['Meta'], attr)
    except (KeyError, AttributeError):
        ret = default
    return ret
            
def get_fieldsets(bases, attrs):
    """
    Get the fieldsets definition from the inner Meta class, mapping it
    on top of the fieldsets from any base classes.

    """
    fieldsets = _get_meta_attr(attrs, 'fieldsets', ())
        
    new_fieldsets = {}
    order = []
    
    for base in bases:
        for fs in getattr(base, 'base_fieldsets', ()):
            new_fieldsets[fs[0]] = fs
            order.append(fs[0])

    for fs in fieldsets:
        new_fieldsets[fs[0]] = fs
        if fs[0] not in order:
            order.append(fs[0])
    
    return [new_fieldsets[name] for name in order]
    

def get_row_attrs(bases, attrs):
    """
    Get the row_attrs definition from the inner Meta class.

    """
    return _get_meta_attr(attrs, 'row_attrs', {})

def _mark_row_attrs(bf, form):
    row_attrs = deepcopy(form._row_attrs.get(bf.name, {}))
    if bf.field.required:
        req_class = 'required'
    else:
        req_class = 'optional'
    if 'class' in row_attrs:
        row_attrs['class'] = row_attrs['class'] + ' ' + req_class
    else:
        row_attrs['class'] = req_class
    bf.row_attrs = mark_safe(flatatt(row_attrs))
    return bf

class BetterFormBaseMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['base_fieldsets'] = get_fieldsets(bases, attrs)
        attrs['base_row_attrs'] = get_row_attrs(bases, attrs)
        new_class = super(BetterFormBaseMetaclass,
                          cls).__new__(cls, name, bases, attrs)
        return new_class

class BetterFormMetaclass(BetterFormBaseMetaclass,
                            forms.forms.DeclarativeFieldsMetaclass):
    pass

class BetterModelFormMetaclass(BetterFormBaseMetaclass,
                                 forms.models.ModelFormMetaclass):
    pass
    
class BetterBaseForm(object):
    """
    ``BetterForm`` and ``BetterModelForm`` are subclasses of Form
    and ModelForm that allow for declarative definition of fieldsets
    and row_attrs in an inner Meta class.

    The row_attrs declaration is a dictionary mapping field names to
    dictionaries of attribute/value pairs.  The attribute/value
    dictionaries will be flattened into HTML-style attribute/values
    (i.e. {'style': 'display: none'} will become ``style="display:
    none"``), and will be available as the ``row_attrs`` attribute of
    the ``BoundField``.  Also, a CSS class of "required" or "optional"
    will automatically be added to the row_attrs of each
    ``BoundField``, depending on whether the field is required.
    
    The fieldsets declaration is a list of two-tuples very similar to
    the ``fieldsets`` option on a ModelAdmin class in
    ``django.contrib.admin``.

    The first item in each two-tuple is a name for the fieldset (must
    be unique, so that overriding fieldsets of superclasses works),
    and the second is a dictionary of fieldset options

    Valid fieldset options in the dictionary include:

    ``fields`` (required): A tuple of field names to display in this
    fieldset.

    ``classes``: A list of extra CSS classes to apply to the fieldset.

    ``legend``: This value, if present, will be the contents of a
    ``legend`` tag to open the fieldset.  If not present the unique
    name of the fieldset will be used (so a value of '' for legend
    must be used if no legend is desired.)

    ``description``: A string of optional extra text to be displayed
    under the ``legend`` of the fieldset.

    When iterated over, the ``fieldsets`` attribute of a
    ``BetterForm`` (or ``BetterModelForm``) yields ``Fieldset``s.
    Each ``Fieldset`` has a name attribute, a legend attribute, and a
    description attribute, and when iterated over yields its
    ``BoundField``s.

    For backwards compatibility, a ``BetterForm`` or
    ``BetterModelForm`` can still be iterated over directly to yield
    all of its ``BoundField``s, regardless of fieldsets.

    For more detailed examples, see the doctests in tests/__init__.py.

    """
    def __init__(self, *args, **kwargs):
        self._fieldsets = deepcopy(self.base_fieldsets)
        self._row_attrs = deepcopy(self.base_row_attrs)
        super(BetterBaseForm, self).__init__(*args, **kwargs)

    @property
    def fieldsets(self):
        return FieldsetCollection(self, self._fieldsets)

    def __iter__(self):
        for bf in super(BetterBaseForm, self).__iter__():
            yield _mark_row_attrs(bf, self)

class BetterForm(BetterBaseForm, forms.Form):
    __metaclass__ = BetterFormMetaclass
    __doc__ = BetterBaseForm.__doc__

class BetterModelForm(BetterBaseForm, forms.ModelForm):
    __metaclass__ = BetterModelFormMetaclass
    __doc__ = BetterBaseForm.__doc__
    

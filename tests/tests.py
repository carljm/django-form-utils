# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django import forms
from django import template
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.fields.files import (
    FieldFile, ImageFieldFile, FileField, ImageField)
from django.test import TestCase
from django.utils import six

from mock import patch

from form_utils.forms import BetterForm, BetterModelForm
from form_utils.widgets import ImageWidget, ClearableFileInput
from form_utils.fields import ClearableFileField, ClearableImageField

from .models import Person, Document


class ApplicationForm(BetterForm):
    """
    A sample form with fieldsets.

    """
    name = forms.CharField()
    position = forms.CharField()
    reference = forms.CharField(required=False)

    class Meta:
        fieldsets = (('main', {'fields': ('name', 'position'), 'legend': ''}),
                     ('Optional', {'fields': ('reference',),
                                   'classes': ('optional',)}))


class InheritedForm(ApplicationForm):
    """
    An inherited form that does not define its own fieldsets inherits
    its parents'.

    """
    pass


class MudSlingerApplicationForm(ApplicationForm):
    """
    Inherited forms can manually inherit and change/override the
    parents' fieldsets by using the logical Python code in Meta:

    """
    target = forms.CharField()

    class Meta:
        fieldsets = list(ApplicationForm.Meta.fieldsets)
        fieldsets[0] = ('main', {'fields': ('name', 'position', 'target'),
                                 'description': 'Basic mudslinging info',
                                 'legend': 'basic info'})


class FeedbackForm(BetterForm):
    """
    A ``BetterForm`` that defines no fieldsets explicitly gets a
    single fieldset by default.

    """
    title = forms.CharField()
    name = forms.CharField()


class HoneypotForm(BetterForm):
    """
    A ``BetterForm`` demonstrating the use of ``row_attrs``.

    In ``django.contrib.comments``, this effect (hiding an entire form
    input along with its label) can only be achieved through a
    customized template; here, we achieve it in a way that allows us
    to still use a generic form-rendering template.

    """
    honeypot = forms.CharField()
    name = forms.CharField()

    class Meta:
        row_attrs = {'honeypot': {'style': 'display: none'}}

    def clean_honeypot(self):
        if self.cleaned_data.get("honeypot"):
            raise forms.ValidationError("Honeypot field must be empty.")


class PersonForm(BetterModelForm):
    """
    A ``BetterModelForm`` with fieldsets.

    """
    title = forms.CharField()

    class Meta:
        model = Person
        fieldsets = [('main', {'fields': ['name'],
                               'legend': '',
                               'classes': ['main']}),
                     ('More', {'fields': ['age'],
                               'description': 'Extra information',
                               'classes': ['more', 'collapse']}),
                     (None, {'fields': ['title']})]


class PartialPersonForm(BetterModelForm):
    """
    A ``BetterModelForm`` whose fieldsets don't contain all fields
    from the model.

    """
    class Meta:
        model = Person
        fieldsets = [('main', {'fields': ['name']})]


class ManualPartialPersonForm(BetterModelForm):
    """
    A ``BetterModelForm`` whose fieldsets don't contain all fields
    from the model, but we set ``fields`` manually.

    """
    class Meta:
        model = Person
        fieldsets = [('main', {'fields': ['name']})]
        fields = ['name', 'age']


class ExcludePartialPersonForm(BetterModelForm):
    """
    A ``BetterModelForm`` whose fieldsets don't contain all fields
    from the model, but we set ``exclude`` manually.

    """
    class Meta:
        model = Person
        fieldsets = [('main', {'fields': ['name']})]
        exclude = ['age']


class AcrobaticPersonForm(PersonForm):
    """
    A ``BetterModelForm`` that inherits from another and overrides one
    of its fieldsets.

    """
    agility = forms.IntegerField()
    speed = forms.IntegerField()

    class Meta(PersonForm.Meta):
        fieldsets = list(PersonForm.Meta.fieldsets)
        fieldsets = fieldsets[:1] + [
            ('Acrobatics', {'fields': ('age', 'speed', 'agility')})]


class AbstractPersonForm(BetterModelForm):
    """
    An abstract ``BetterModelForm`` without fieldsets.

    """
    title = forms.CharField()

    class Meta:
        pass


class InheritedMetaAbstractPersonForm(AbstractPersonForm):
    """
    A ``BetterModelForm`` that inherits from abstract one and its Meta class
    and adds fieldsets

    """
    class Meta(AbstractPersonForm.Meta):
        model = Person
        fieldsets = [('main', {'fields': ['name'],
                               'legend': '',
                               'classes': ['main']}),
                     ('More', {'fields': ['age'],
                               'description': 'Extra information',
                               'classes': ['more', 'collapse']}),
                     (None, {'fields': ['title']})]


class BetterFormTests(TestCase):
    fieldset_target_data = {
        ApplicationForm:
            [
                    (['name', 'position'],
                     {
                                'name': 'main',
                                'legend': '',
                                'description': '',
                                'classes': '',
                                }),
                    (['reference'],
                    {
                                'name': 'Optional',
                                'legend': 'Optional',
                                'description': '',
                                'classes': 'optional'
                                }),
                    ],
        InheritedForm:
            [
                    (['name', 'position'],
                     {
                                'name': 'main',
                                'legend': '',
                                'description': '',
                                'classes': '',
                                }),
                    (['reference'],
                    {
                                'name': 'Optional',
                                'legend': 'Optional',
                                'description': '',
                                'classes': 'optional'
                                }),
                    ],
        MudSlingerApplicationForm:
            [
                    (['name', 'position', 'target'],
                     {
                                'name': 'main',
                                'legend': 'basic info',
                                'description': 'Basic mudslinging info',
                                'classes': '',
                                }),
                    (['reference'],
                    {
                                'name': 'Optional',
                                'legend': 'Optional',
                                'description': '',
                                'classes': 'optional'
                                }),
                    ],
        FeedbackForm:
            [
                    (['title', 'name'],
                     {
                                'name': 'main',
                                'legend': '',
                                'description': '',
                                'classes': '',
                                }),
                    ],
        PersonForm:
            [
                    (['name'],
                     {
                                'name': 'main',
                                'legend': '',
                                'description': '',
                                'classes': 'main',
                                }),
                    (['age'],
                    {
                                'name': 'More',
                                'legend': 'More',
                                'description': 'Extra information',
                                'classes': 'more collapse'
                                }),
                    (['title'],
                    {
                                'name': None,
                                'legend': None,
                                'description': '',
                                'classes': ''
                                }),
                    ],
        AcrobaticPersonForm:
            [
                    (['name'],
                     {
                                'name': 'main',
                                'legend': '',
                                'description': '',
                                'classes': 'main',
                                }),
                    (['age', 'speed', 'agility'],
                    {
                                'name': 'Acrobatics',
                                'legend': 'Acrobatics',
                                'description': '',
                                'classes': ''
                                }),
                    ],
            InheritedMetaAbstractPersonForm:
            [
                    (['name'],
                     {
                                'name': 'main',
                                'legend': '',
                                'description': '',
                                'classes': 'main',
                                }),
                    (['age'],
                    {
                                'name': 'More',
                                'legend': 'More',
                                'description': 'Extra information',
                                'classes': 'more collapse'
                                }),
                    (['title'],
                    {
                                'name': None,
                                'legend': None,
                                'description': '',
                                'classes': ''
                                }),
                    ],


        }

    def test_iterate_fieldsets(self):
        """
        Test the definition and inheritance of fieldsets, by matching
        sample form classes' ``fieldsets`` attribute with the target
        data in ``self.fieldsets_target_data``.

        """
        for form_class, targets in self.fieldset_target_data.items():
            form = form_class()
            # verify len(form.fieldsets) tells us the truth
            self.assertEqual(len(form.fieldsets), len(targets))
            for i, fs in enumerate(form.fieldsets):
                target_data = targets[i]
                # verify fieldset contains correct fields
                self.assertEqual([f.name for f in fs],
                                  target_data[0])
                # verify fieldset has correct attributes
                for attr, val in target_data[1].items():
                    self.assertEqual(getattr(fs, attr), val)

    def test_fieldset_errors(self):
        """
        We can access the ``errors`` attribute of a bound form and get
        an ``ErrorDict``.

        """
        form = ApplicationForm(data={'name': 'John Doe',
                                     'reference': 'Jane Doe'})
        self.assertEqual([fs.errors for fs in form.fieldsets],
                          [{'position': [u'This field is required.']}, {}])

    def test_iterate_fields(self):
        """
        We can still iterate over a ``BetterForm`` and get its fields
        directly, regardless of fieldsets (backward-compatibility with
        regular ``Forms``).

        """
        form = ApplicationForm()
        self.assertEqual([field.name for field in form],
                          ['name', 'position', 'reference'])

    def test_getitem_fields(self):
        """
        We can use dictionary style look up of fields in a fieldset using the
        name as the key.

        """
        form = ApplicationForm()
        fieldset = form.fieldsets['main']
        self.assertEqual(fieldset.name, 'main')
        self.assertEqual(len(fieldset.boundfields), 2)

    def test_row_attrs_by_name(self):
        """
        Fields of a ``BetterForm`` accessed by name have ``row_attrs``
        as defined in the inner ``Meta`` class.

        """
        form = HoneypotForm()
        attrs = form['honeypot'].row_attrs
        self.assertTrue(u'style="display: none"' in attrs)
        self.assertTrue(u'class="required"' in attrs)

    def test_row_attrs_by_iteration(self):
        """
        Fields of a ``BetterForm`` accessed by form iteration have
        ``row_attrs`` as defined in the inner ``Meta`` class.

        """
        form = HoneypotForm()
        honeypot = [field for field in form if field.name=='honeypot'][0]
        attrs = honeypot.row_attrs
        self.assertTrue(u'style="display: none"' in attrs)
        self.assertTrue(u'class="required"' in attrs)

    def test_row_attrs_by_fieldset_iteration(self):
        """
        Fields of a ``BetterForm`` accessed by fieldset iteration have
        ``row_attrs`` as defined in the inner ``Meta`` class.

        """
        form = HoneypotForm()
        fieldset = [fs for fs in form.fieldsets][0]
        honeypot = [field for field in fieldset if field.name=='honeypot'][0]
        attrs = honeypot.row_attrs
        self.assertTrue(u'style="display: none"' in attrs)
        self.assertTrue(u'class="required"' in attrs)

    def test_row_attrs_error_class(self):
        """
        row_attrs adds an error class if a field has errors.

        """
        form = HoneypotForm({"honeypot": "something"})

        attrs = form['honeypot'].row_attrs
        self.assertTrue(u'style="display: none"' in attrs)
        self.assertTrue(u'class="required error"' in attrs)

    def test_friendly_typo_error(self):
        """
        If we define a single fieldset and leave off the trailing , in
        a tuple, we get a friendly error.

        """
        def _define_fieldsets_with_missing_comma():
            class ErrorForm(BetterForm):
                one = forms.CharField()
                two = forms.CharField()
                class Meta:
                    fieldsets = ((None, {'fields': ('one', 'two')}))
        # can't test the message here, but it would be TypeError otherwise
        self.assertRaises(ValueError,
                          _define_fieldsets_with_missing_comma)

    def test_modelform_fields(self):
        """
        The ``fields`` Meta option of a ModelForm is automatically
        populated with the fields present in a fieldsets definition.

        """
        self.assertEqual(PartialPersonForm._meta.fields, ['name'])

    def test_modelform_manual_fields(self):
        """
        The ``fields`` Meta option of a ModelForm is not automatically
        populated if it's set manually.

        """
        self.assertEqual(ManualPartialPersonForm._meta.fields, ['name', 'age'])

    def test_modelform_fields_exclude(self):
        """
        The ``fields`` Meta option of a ModelForm is not automatically
        populated if ``exclude`` is set manually.

        """
        self.assertEqual(ExcludePartialPersonForm._meta.fields, None)


number_field_type = 'number' if django.VERSION > (1, 6, 0) else 'text'
label_suffix = ':' if django.VERSION > (1, 6, 0) else ''


class BoringForm(forms.Form):
    boredom = forms.IntegerField()
    excitement = forms.IntegerField()

class TemplatetagTests(TestCase):
    boring_form_html = (
        u'<fieldset class="fieldset_main">'
        u'<ul>'
        u'<li>'
        u'<label for="id_boredom">Boredom%(suffix)s</label>'
        u'<input type="%(type)s" name="boredom" id="id_boredom" />'
        u'</li>'
        u'<li>'
        u'<label for="id_excitement">Excitement%(suffix)s</label>'
        u'<input type="%(type)s" name="excitement" id="id_excitement" />'
        u'</li>'
        u'</ul>'
        u'</fieldset>'
        ) % {'type': number_field_type, 'suffix': label_suffix}

    def test_render_form(self):
        """
        A plain ``forms.Form`` renders as a list of fields.

        """
        form = BoringForm()
        tpl = template.Template('{% load form_utils %}{{ form|render }}')
        html = tpl.render(template.Context({'form': form}))
        self.assertHTMLEqual(html, self.boring_form_html)

    betterform_html = (
        u'<fieldset class="">'
        u'<ul>'
        u'<li class="required">'
        u'<label for="id_name">Name%(suffix)s</label>'
        u'<input type="text" name="name" id="id_name" />'
        u'</li>'
        u'<li class="required">'
        u'<label for="id_position">Position%(suffix)s</label>'
        u'<input type="text" name="position" id="id_position" />'
        u'</li>'
        u'</ul>'
        u'</fieldset>'
        u'<fieldset class="optional">'
        u'<legend>Optional</legend>'
        u'<ul>'
        u'<li class="optional">'
        u'<label for="id_reference">Reference%(suffix)s</label>'
        u'<input type="text" name="reference" id="id_reference" />'
        u'</li>'
        u'</ul>'
        u'</fieldset>'
        ) % {'suffix': label_suffix}

    def test_render_betterform(self):
        """
        A ``BetterForm`` renders as a list of fields within each fieldset.

        """
        form = ApplicationForm()
        tpl = template.Template('{% load form_utils %}{{ form|render }}')
        html = tpl.render(template.Context({'form': form}))
        self.assertHTMLEqual(html, self.betterform_html)


class ImageWidgetTests(TestCase):
    def test_render(self):
        """
        ``ImageWidget`` renders the file input and the image thumb.

        """
        widget = ImageWidget()
        html = widget.render('fieldname', ImageFieldFile(None, ImageField(), 'tiny.png'))
        # test only this much of the html, because the remainder will
        # vary depending on whether we have sorl-thumbnail
        self.assertTrue('<img' in html)
        self.assertTrue('/media/tiny' in html)

    def test_render_nonimage(self):
        """
        ``ImageWidget`` renders the file input only, if given a non-image.

        """
        widget = ImageWidget()
        html = widget.render('fieldname', FieldFile(None, FileField(), 'something.txt'))
        self.assertHTMLEqual(html, '<input type="file" name="fieldname" />')

    def test_custom_template(self):
        """
        ``ImageWidget`` respects a custom template.

        """
        widget = ImageWidget(template='<div>%(image)s</div>'
                             '<div>%(input)s</div>')
        html = widget.render('fieldname', ImageFieldFile(None, ImageField(), 'tiny.png'))
        self.assertTrue(html.startswith('<div><img'))


class ClearableFileInputTests(TestCase):
    def test_render(self):
        """
        ``ClearableFileInput`` renders the file input and an unchecked
        clear checkbox.

        """
        widget = ClearableFileInput()
        html = widget.render('fieldname', 'tiny.png')
        self.assertHTMLEqual(
            html,
            '<input type="file" name="fieldname_0" />'
            ' Clear: '
            '<input type="checkbox" name="fieldname_1" />'
            )

    def test_custom_file_widget(self):
        """
        ``ClearableFileInput`` respects its ``file_widget`` argument.

        """
        widget = ClearableFileInput(file_widget=ImageWidget())
        html = widget.render('fieldname', ImageFieldFile(None, ImageField(), 'tiny.png'))
        self.assertTrue('<img' in html)

    def test_custom_file_widget_via_subclass(self):
        """
        Default ``file_widget`` class can also be customized by
        subclassing.

        """
        class ClearableImageWidget(ClearableFileInput):
            default_file_widget_class = ImageWidget
        widget = ClearableImageWidget()
        html = widget.render('fieldname', ImageFieldFile(None, ImageField(), 'tiny.png'))
        self.assertTrue('<img' in html)

    def test_custom_template(self):
        """
        ``ClearableFileInput`` respects its ``template`` argument.

        """
        widget = ClearableFileInput(template='Clear: %(checkbox)s %(input)s')
        html = widget.render('fieldname', ImageFieldFile(None, ImageField(), 'tiny.png'))
        self.assertHTMLEqual(
            html,
            'Clear: '
            '<input type="checkbox" name="fieldname_1" /> '
            '<input type="file" name="fieldname_0" />'
            )

    def test_custom_template_via_subclass(self):
        """
        Template can also be customized by subclassing.

        """
        class ReversedClearableFileInput(ClearableFileInput):
            template = 'Clear: %(checkbox)s %(input)s'
        widget = ReversedClearableFileInput()
        html = widget.render('fieldname', 'tiny.png')
        self.assertHTMLEqual(
            html,
            'Clear: '
            '<input type="checkbox" name="fieldname_1" /> '
            '<input type="file" name="fieldname_0" />'
            )


class ClearableFileFieldTests(TestCase):
    upload = SimpleUploadedFile('something.txt', b'Something')

    def test_bound_redisplay(self):
        class TestForm(forms.Form):
            f = ClearableFileField()
        form = TestForm(files={'f_0': self.upload})
        self.assertHTMLEqual(
            six.text_type(form['f']),
            u'<input type="file" name="f_0" id="id_f_0" />'
            u' Clear: <input type="checkbox" name="f_1" id="id_f_1" />'
            )

    def test_not_cleared(self):
        """
        If the clear checkbox is not checked, the ``FileField`` data
        is returned normally.

        """
        field = ClearableFileField()
        result = field.clean([self.upload, '0'])
        self.assertEqual(result, self.upload)

    def test_cleared(self):
        """
        If the clear checkbox is checked and the file input empty, the
        field returns a value that is able to get a normal model
        ``FileField`` to clear itself.

        This is actually a bit tricky/hacky in the implementation, see
        the docstring of ``form_utils.fields.FakeEmptyFieldFile`` for
        details. Here we just test the results.

        """
        doc = Document.objects.create(myfile='something.txt')
        field = ClearableFileField(required=False)
        result = field.clean(['', '1'])
        doc._meta.get_field('myfile').save_form_data(doc, result)
        doc.save()
        doc = Document.objects.get(pk=doc.pk)
        self.assertEqual(doc.myfile, '')

    def test_cleared_but_file_given(self):
        """
        If we check the clear checkbox, but also submit a file, the
        file overrides.

        """
        field = ClearableFileField()
        result = field.clean([self.upload, '1'])
        self.assertEqual(result, self.upload)

    def test_custom_file_field(self):
        """
        We can pass in our own ``file_field`` rather than using the
        default ``forms.FileField``.

        """
        file_field = forms.ImageField()
        field = ClearableFileField(file_field=file_field)
        self.assertTrue(field.fields[0] is file_field)

    def test_custom_file_field_required(self):
        """
        If we pass in our own ``file_field`` its required value is
        used for the composite field.

        """
        file_field = forms.ImageField(required=False)
        field = ClearableFileField(file_field=file_field)
        self.assertFalse(field.required)

    def test_custom_file_field_widget_used(self):
        """
        If we pass in our own ``file_field`` its widget is used for
        the internal file field.

        """
        widget = ImageWidget()
        file_field = forms.ImageField(widget=widget)
        field = ClearableFileField(file_field=file_field)
        self.assertTrue(field.fields[0].widget is widget)

    def test_clearable_image_field(self):
        """
        We can override the default ``file_field`` class by
        subclassing.

        ``ClearableImageField`` is provided, and does just this.

        """
        field = ClearableImageField()
        self.assertTrue(isinstance(field.fields[0], forms.ImageField))

    def test_custom_template(self):
        """
        We can pass in a custom template and it will be passed on to
        the widget.

        """
        tpl = 'Clear: %(checkbox)s %(input)s'
        field = ClearableFileField(template=tpl)
        self.assertEqual(field.widget.template, tpl)

    def test_custom_widget_by_subclassing(self):
        """
        We can set a custom default widget by subclassing.

        """
        class ClearableImageWidget(ClearableFileInput):
            default_file_widget_class = ImageWidget
        class ClearableImageWidgetField(ClearableFileField):
            widget = ClearableImageWidget
        field = ClearableImageWidgetField()
        self.assertTrue(isinstance(field.widget, ClearableImageWidget))




class FieldFilterTests(TestCase):
    """Tests for form field filters."""
    @property
    def form_utils(self):
        """The module under test."""
        from form_utils.templatetags import form_utils
        return form_utils


    @property
    def form(self):
        """A sample form."""
        class PersonForm(forms.Form):
            name = forms.CharField(initial="none", required=True)
            level = forms.ChoiceField(
                choices=(("b", "Beginner"), ("a", "Advanced")), required=False)
            colors = forms.MultipleChoiceField(
                choices=[("red", "red"), ("blue", "blue")])
            gender = forms.ChoiceField(
                choices=(("m", "Male"), ("f", "Female"), ("o", "Other")),
                widget=forms.RadioSelect(),
                required=False,
                )
            awesome = forms.BooleanField(required=False)

        return PersonForm


    @patch("form_utils.templatetags.form_utils.render_to_string")
    def test_label(self, render_to_string):
        """``label`` filter renders field label from template."""
        render_to_string.return_value = "<label>something</label>"
        bf = self.form()["name"]

        label = self.form_utils.label(bf)

        self.assertEqual(label, "<label>something</label>")
        render_to_string.assert_called_with(
            "forms/_label.html",
            {
                "label_text": "Name",
                "id": "id_name",
                "field": bf
                }
            )


    @patch("form_utils.templatetags.form_utils.render_to_string")
    def test_label_override(self, render_to_string):
        """label filter allows overriding the label text."""
        bf = self.form()["name"]

        self.form_utils.label(bf, "override")

        render_to_string.assert_called_with(
            "forms/_label.html",
            {
                "label_text": "override",
                "id": "id_name",
                "field": bf
                }
            )


    def test_value_text(self):
        """``value_text`` filter returns value of field."""
        self.assertEqual(
            self.form_utils.value_text(self.form({"name": "boo"})["name"]), "boo")


    def test_value_text_unbound(self):
        """``value_text`` filter returns default value of unbound field."""
        self.assertEqual(self.form_utils.value_text(self.form()["name"]), "none")


    def test_value_text_choices(self):
        """``value_text`` filter returns human-readable value of choicefield."""
        self.assertEqual(
            self.form_utils.value_text(
                self.form({"level": "a"})["level"]), "Advanced")


    def test_selected_values_choices(self):
        """``selected_values`` filter returns values of multiple select."""
        f = self.form({"level": ["a", "b"]})

        self.assertEqual(
            self.form_utils.selected_values(f["level"]),
            ["Advanced", "Beginner"],
            )


    def test_optional_false(self):
        """A required field should not be marked optional."""
        self.assertFalse(self.form_utils.optional(self.form()["name"]))


    def test_optional_true(self):
        """A non-required field should be marked optional."""
        self.assertTrue(self.form_utils.optional(self.form()["level"]))


    def test_detect_checkbox(self):
        """``is_checkbox`` detects checkboxes."""
        f = self.form()

        self.assertTrue(self.form_utils.is_checkbox(f["awesome"]))


    def test_detect_non_checkbox(self):
        """``is_checkbox`` detects that select fields are not checkboxes."""
        f = self.form()

        self.assertFalse(self.form_utils.is_checkbox(f["level"]))


    def test_is_multiple(self):
        """`is_multiple` detects a MultipleChoiceField."""
        f = self.form()

        self.assertTrue(self.form_utils.is_multiple(f["colors"]))


    def test_is_not_multiple(self):
        """`is_multiple` detects a non-multiple widget."""
        f = self.form()

        self.assertFalse(self.form_utils.is_multiple(f["level"]))


    def test_is_select(self):
        """`is_select` detects a ChoiceField."""
        f = self.form()

        self.assertTrue(self.form_utils.is_select(f["level"]))


    def test_is_not_select(self):
        """`is_select` detects a non-ChoiceField."""
        f = self.form()

        self.assertFalse(self.form_utils.is_select(f["name"]))


    def test_is_radio(self):
        """`is_radio` detects a radio select widget."""
        f = self.form()

        self.assertTrue(self.form_utils.is_radio(f["gender"]))


    def test_is_not_radio(self):
        """`is_radio` detects a non-radio select."""
        f = self.form()

        self.assertFalse(self.form_utils.is_radio(f["level"]))

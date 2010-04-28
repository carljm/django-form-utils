from django import forms
from django import template
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from form_utils.forms import BetterForm, BetterModelForm
from form_utils.widgets import ImageWidget, ClearableFileInput
from form_utils.fields import ClearableFileField, ClearableImageField

from models import Person, Document

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
        fieldsets = fieldsets[:1] + \
                     [('Acrobatics', {'fields': ('age', 'speed', 'agility')})]

                     
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
            self.assertEquals(len(form.fieldsets), len(targets))
            for i, fs in enumerate(form.fieldsets):
                target_data = targets[i]
                # verify fieldset contains correct fields
                self.assertEquals([f.name for f in fs],
                                  target_data[0])
                # verify fieldset has correct attributes
                for attr, val in target_data[1].items():
                    self.assertEquals(getattr(fs, attr), val)
        
    def test_fieldset_errors(self):
        """
        We can access the ``errors`` attribute of a bound form and get
        an ``ErrorDict``.

        """
        form = ApplicationForm(data={'name': 'John Doe',
                                     'reference': 'Jane Doe'})
        self.assertEquals([fs.errors for fs in form.fieldsets],
                          [{'position': [u'This field is required.']}, {}])

    def test_iterate_fields(self):
        """
        We can still iterate over a ``BetterForm`` and get its fields
        directly, regardless of fieldsets (backward-compatibility with
        regular ``Forms``).

        """
        form = ApplicationForm()
        self.assertEquals([field.name for field in form],
                          ['name', 'position', 'reference'])

    def test_getitem_fields(self):
        """
        We can use dictionary style look up of fields in a fieldset using the
        name as the key.

        """
        form = ApplicationForm()
        fieldset = form.fieldsets['main']
        self.assertEquals(fieldset.name, 'main')
        self.assertEquals(len(fieldset.boundfields), 2)

    def test_row_attrs_by_name(self):
        """
        Fields of a ``BetterForm`` accessed by name have ``row_attrs``
        as defined in the inner ``Meta`` class.

        """
        form = HoneypotForm()
        self.assertEquals(form['honeypot'].row_attrs,
                          u' style="display: none" class="required"')

    def test_row_attrs_by_iteration(self):
        """
        Fields of a ``BetterForm`` accessed by form iteration have
        ``row_attrs`` as defined in the inner ``Meta`` class.

        """
        form = HoneypotForm()
        honeypot = [field for field in form if field.name=='honeypot'][0]
        self.assertEquals(honeypot.row_attrs,
                          u' style="display: none" class="required"')

    def test_row_attrs_by_fieldset_iteration(self):
        """
        Fields of a ``BetterForm`` accessed by fieldset iteration have
        ``row_attrs`` as defined in the inner ``Meta`` class.

        """
        form = HoneypotForm()
        fieldset = [fs for fs in form.fieldsets][0]
        honeypot = [field for field in fieldset if field.name=='honeypot'][0]
        self.assertEquals(honeypot.row_attrs,
                          u' style="display: none" class="required"')

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
        self.assertEquals(PartialPersonForm._meta.fields, ['name'])

    def test_modelform_manual_fields(self):
        """
        The ``fields`` Meta option of a ModelForm is not automatically
        populated if it's set manually.

        """
        self.assertEquals(ManualPartialPersonForm._meta.fields, ['name', 'age'])

    def test_modelform_fields(self):
        """
        The ``fields`` Meta option of a ModelForm is not automatically
        populated if ``exclude`` is set manually.

        """
        self.assertEquals(ExcludePartialPersonForm._meta.fields, None)


class BoringForm(forms.Form):
    boredom = forms.IntegerField()
    excitement = forms.IntegerField()
                          
class TemplatetagTests(TestCase):
    boring_form_html = [
        u'<fieldset class="fieldset_main">',
        u'<ul>',
        u'<li>',
        u'<label for="id_boredom">',
        u'Boredom',
        u'</label>',
        u'<input type="text" name="boredom" id="id_boredom" />',
        u'</li>',
        u'<li>',
        u'<label for="id_excitement">',
        u'Excitement',
        u'</label>',
        u'<input type="text" name="excitement" id="id_excitement" />',
        u'</li>',
        u'</ul>',
        u'</fieldset>',
        ]
        
    def test_render_form(self):
        """
        A plain ``forms.Form`` renders as a list of fields.

        """
        form = BoringForm()
        tpl = template.Template('{% load form_utils_tags %}{{ form|render }}')
        html = tpl.render(template.Context({'form': form}))
        self.assertEquals([l.strip() for l in html.splitlines() if l.strip()],
                          self.boring_form_html)

    betterform_html = [
        u'<fieldset class="">',
        u'<ul>',
        u'<li class="required">',
        u'<label for="id_name">',
        u'Name',
        u'</label>',
        u'<input type="text" name="name" id="id_name" />',
        u'</li>',
        u'<li class="required">',
        u'<label for="id_position">',
        u'Position',
        u'</label>',
        u'<input type="text" name="position" id="id_position" />',
        u'</li>',
        u'</ul>',
        u'</fieldset>',
        u'<fieldset class="optional">',
        u'<legend>Optional</legend>',
        u'<ul>',
        u'<li class="optional">',
        u'<label for="id_reference">',
        u'Reference',
        u'</label>',
        u'<input type="text" name="reference" id="id_reference" />',
        u'</li>',
        u'</ul>',
        u'</fieldset>'
        ]

    def test_render_betterform(self):
        """
        A ``BetterForm`` renders as a list of fields within each fieldset.

        """
        form = ApplicationForm()
        tpl = template.Template('{% load form_utils_tags %}{{ form|render }}')
        html = tpl.render(template.Context({'form': form}))
        self.assertEquals([l.strip() for l in html.splitlines() if l.strip()],
                          self.betterform_html)


class ImageWidgetTests(TestCase):
    def test_render(self):
        """
        ``ImageWidget`` renders the file input and the image thumb.

        """
        widget = ImageWidget()
        html = widget.render('fieldname', 'tiny.png')
        # test only this much of the html, because the remainder will
        # vary depending on whether we have sorl-thumbnail
        self.failUnless(html.startswith(
                '<input type="file" name="fieldname" value="tiny.png" />'
                '<br /><img src="/media/tiny'))

    def test_custom_template(self):
        """
        ``ImageWidget`` respects a custom template.

        """
        widget = ImageWidget(template='<div>%(image)s</div>'
                             '<div>%(input)s</div>')
        html = widget.render('fieldname', 'tiny.png')
        self.failUnless(html.startswith('<div><img src="/media/tiny'))


class ClearableFileInputTests(TestCase):
    def test_render(self):
        """
        ``ClearableFileInput`` renders the file input and an unchecked
        clear checkbox.

        """
        widget = ClearableFileInput()
        html = widget.render('fieldname', 'tiny.png')
        self.assertEquals(html,
                          '<input type="file" name="fieldname_0" />'
                          ' Clear: '
                          '<input type="checkbox" name="fieldname_1" />')

    def test_custom_file_widget(self):
        """
        ``ClearableFileInput`` respects its ``file_widget`` argument.

        """
        widget = ClearableFileInput(file_widget=ImageWidget())
        html = widget.render('fieldname', 'tiny.png')
        self.failUnless(html.startswith(
                '<input type="file" name="fieldname_0" value="tiny.png" />'
                '<br /><img src="/media/tiny'))

    def test_custom_file_widget_via_subclass(self):
        """
        Default ``file_widget`` class can also be customized by
        subclassing.

        """
        class ClearableImageWidget(ClearableFileInput):
            default_file_widget_class = ImageWidget
        widget = ClearableImageWidget()
        html = widget.render('fieldname', 'tiny.png')
        self.failUnless(html.startswith(
                '<input type="file" name="fieldname_0" value="tiny.png" />'
                '<br /><img src="/media/tiny'))

    def test_custom_template(self):
        """
        ``ClearableFileInput`` respects its ``template`` argument.

        """
        widget = ClearableFileInput(template='Clear: %(checkbox)s %(input)s')
        html = widget.render('fieldname', 'tiny.png')
        self.assertEquals(html,
                          'Clear: '
                          '<input type="checkbox" name="fieldname_1" /> '
                          '<input type="file" name="fieldname_0" />')
                          
    def test_custom_template_via_subclass(self):
        """
        Template can also be customized by subclassing.

        """
        class ReversedClearableFileInput(ClearableFileInput):
            template = 'Clear: %(checkbox)s %(input)s'
        widget = ReversedClearableFileInput()
        html = widget.render('fieldname', 'tiny.png')
        self.assertEquals(html,
                          'Clear: '
                          '<input type="checkbox" name="fieldname_1" /> '
                          '<input type="file" name="fieldname_0" />')
                          

class ClearableFileFieldTests(TestCase):
    upload = SimpleUploadedFile('something.txt', 'Something')
    
    def test_not_cleared(self):
        """
        If the clear checkbox is not checked, the ``FileField`` data
        is returned normally.

        """
        field = ClearableFileField()
        result = field.clean([self.upload, '0'])
        self.assertEquals(result, self.upload)

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
        self.assertEquals(doc.myfile, '')

    def test_cleared_but_file_given(self):
        """
        If we check the clear checkbox, but also submit a file, the
        file overrides.

        """
        field = ClearableFileField()
        result = field.clean([self.upload, '1'])
        self.assertEquals(result, self.upload)

    def test_custom_file_field(self):
        """
        We can pass in our own ``file_field`` rather than using the
        default ``forms.FileField``.

        """
        file_field = forms.ImageField()
        field = ClearableFileField(file_field=file_field)
        self.failUnless(field.fields[0] is file_field)

    def test_custom_file_field_required(self):
        """
        If we pass in our own ``file_field`` its required value is
        used for the composite field.

        """
        file_field = forms.ImageField(required=False)
        field = ClearableFileField(file_field=file_field)
        self.failIf(field.required)

    def test_custom_file_field_widget_used(self):
        """
        If we pass in our own ``file_field`` its widget is used for
        the internal file field.

        """
        widget = ImageWidget()
        file_field = forms.ImageField(widget=widget)
        field = ClearableFileField(file_field=file_field)
        self.failUnless(field.fields[0].widget is widget)

    def test_clearable_image_field(self):
        """
        We can override the default ``file_field`` class by
        subclassing.

        ``ClearableImageField`` is provided, and does just this.

        """
        field = ClearableImageField()
        self.failUnless(isinstance(field.fields[0], forms.ImageField))

    def test_custom_template(self):
        """
        We can pass in a custom template and it will be passed on to
        the widget.

        """
        tpl = 'Clear: %(checkbox)s %(input)s'
        field = ClearableFileField(template=tpl)
        self.assertEquals(field.widget.template, tpl)

    def test_custom_widget_by_subclassing(self):
        """
        We can set a custom default widget by subclassing.

        """
        class ClearableImageWidget(ClearableFileInput):
            default_file_widget_class = ImageWidget
        class ClearableImageWidgetField(ClearableFileField):
            widget = ClearableImageWidget
        field = ClearableImageWidgetField()
        self.failUnless(isinstance(field.widget, ClearableImageWidget))

        

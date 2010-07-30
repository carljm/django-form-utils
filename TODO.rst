django-form-utils TODO
======================

ClearableFileField
~~~~~~~~~~~~~~~~~~

Behavior on bound-redisplay is a bit funky, because of hardcoded
special-casing of FileField in Django's forms.py. FileField's are
special-cased in BaseForm._clean_fields to receive initial (in
addition to submitted) data in their clean() method, and also in
BoundField.as_widget() to have initial data rendered as the value if
no new data was submitted. Since we inherit from MultiValueField
rather than FileField, we don't get this special-casing, and so our
FileField always renders empty on bound redisplay when a regular
FileField would render the initial data.

Ideally Django would be fixed to remove this special-casing of
FileField, either making it polymorphic behavior on fields/widgets or
based on a Field class attribute flag, or some such. Then we could
pretend to be a FileField and be able to emulate that behavior.

CHANGES
=======

tip (unreleased)
----------------

1.0.3 (2015-08-25)
------------------

- Fixed compatibility with Django 1.9. Fixed GH-12.

1.0.2 (2014-09-08)
------------------

- Fixed compatibility with Django 1.7. Fixed BB-20 and GH-8.

1.0.1 (2013-10-19)
------------------

- Removed invalid uses of ``python_2_unicode_compatible`` that broke with
  https://github.com/django/django/commit/589dc49e129f63801c54c15e408c944a345b3dfe
  Thanks ocZio for the report.

- Fixed inheritance of form Meta class. Thanks chmodas. Fixed BB-16.

1.0 (2013.08.22)
----------------

- Add Python 3.3 compatibility. Thanks chmodas! (Merge of GH-5.)

0.3.1 (2013.06.25)
------------------

- Call ``FileInput.render`` from ``ImageWidget.render``, ensuring no value is
  output in HTML. Fixes GH-4. Thanks Aron Griffis.

0.3.0 (2013.06.04)
------------------

- BACKWARDS-INCOMPATIBLE: Renamed template tag library from ``form_utils_tags``
  to ``form_utils``.

- BACKWARDS-INCOMPATIBLE: Removed ``FORM_UTILS_MEDIA_URL`` setting and updated
  to use ``STATIC_URL`` rather than ``MEDIA_URL`` throughout.

- Added "error" class to row_attrs for fields with errors. Thanks Aron
  Griffis.

- Dropped explicit support for Django versions prior to 1.4 and Python
  versions prior to 2.6.

0.2.0 (2011.01.28)
------------------

- Add width and height arguments to ImageWidget.

- Make ImageWidget image-detection backend-friendly, no direct use of
  PIL. Fixes issue #7.

- Fix default templates' rendering of labels for radio/checkbox inputs.

- Fix error redisplaying bound form with ClearableFileField.

- Automatically set ``fields`` on ``BetterModelForm`` to list of fields
  present in ``fieldsets``, if ``fields`` or ``exclude`` are not set
  manually.

- Updated to allow ``__getitem__`` access to fieldsets.

0.1.8 (2010.03.16)
------------------

- Restrict PIL import to ImageWidget only

- Added AutoResizeTextarea

0.1.7 (2009.12.02)
------------------

- Fix ClearableFileField import in admin.py.

0.1.6 (2009.11.24)
------------------

- Added documentation and tests for ``ImageWidget`` and
  ``ClearableFileField``.

- Moved ``ClearableFileField`` from ``widgets.py`` to ``fields.py``.

- Converted doctests to unittests.

0.1.5 (2009.11.10)
--------------------------

- Added fieldset classes (previously existed only as a figment of the
  documentation).

0.1.0 (2009-03-26)
------------------

- Initial public release.

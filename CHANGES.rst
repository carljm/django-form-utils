CHANGES
=======

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

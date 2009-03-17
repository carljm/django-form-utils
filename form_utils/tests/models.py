"""
models for django-form-utils tests

Time-stamp: <2008-10-13 10:42:02 carljm models.py>

"""
from django.db import models

class FieldsetTestModel(models.Model):
    one = models.IntegerField()
    two = models.IntegerField()


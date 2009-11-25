from django.db import models

class Person(models.Model):
    age = models.IntegerField()
    name = models.CharField(max_length=100)


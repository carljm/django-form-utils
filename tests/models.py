from django.db import models

class Person(models.Model):
    age = models.IntegerField()
    name = models.CharField(max_length=100)

class Document(models.Model):
    myfile = models.FileField(upload_to='uploads')
    

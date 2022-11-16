from django.db import models

# Create your models here.

class SomeModel(models.Model):
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.name

class NumberOfSomeModelItems(models.Model):
    count = models.PositiveSmallIntegerField()
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.count
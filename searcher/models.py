from __future__ import unicode_literals

from django.db import models

class Page(models.Model):
    url = models.CharField(max_length=255, primary_key=True)
    text = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.url

class index(models.Model):
    word = models.CharField(max_length=255, primary_key=True)
    url = models.ManyToManyField(Page, blank=True)

    def __str__(self):
        return self.word

# models.py
from django.db import models

class Resume(models.Model):
    job_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    education = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    projects = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

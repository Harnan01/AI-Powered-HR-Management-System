from django.db import models

# Create your models here.
from django.db import models


class Interview(models.Model):
    candidate_name = models.CharField(max_length=255)
    interview_date = models.DateTimeField()
    interview_notes = models.TextField()
    result = models.CharField(max_length=50)

    def __str__(self):
        return self.candidate_name

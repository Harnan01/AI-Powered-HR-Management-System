from django.db import models

# Create your models here.
from django.db import models


class Evaluation(models.Model):
    candidate_name = models.CharField(max_length=255)
    score = models.IntegerField()
    feedback = models.TextField()

    def __str__(self):
        return self.candidate_name

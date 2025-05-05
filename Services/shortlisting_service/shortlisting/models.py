from django.db import models


class ShortlistingRequest(models.Model):
    job_id = models.CharField(max_length=36)  # Adjust the max_length as needed
    num_candidates = models.IntegerField()
    # Add other fields if necessary




class ShortlistedCandidate(models.Model):
    job_id = models.CharField(max_length=36)   # Ensure consistency with ShortlistingRequest
    resume_id = models.CharField(max_length=24)
    score = models.CharField(max_length=10)  # Change to CharField with a suitable max_length
    explanation = models.TextField(null=True, blank=True)

    # Add other fields if necessary

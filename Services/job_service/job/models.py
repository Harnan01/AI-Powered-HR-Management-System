from djongo import models
from bson import ObjectId
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Job(models.Model):
    _id = models.ObjectIdField(primary_key=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.title

@receiver(pre_save, sender=Job)
def ensure_id(sender, instance, **kwargs):
    if not instance._id:
        instance._id = ObjectId()

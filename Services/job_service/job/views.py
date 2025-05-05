from rest_framework import viewsets
from django.http import Http404  # Import Http404
from .models import Job
from .serializers import JobSerializer
from bson import ObjectId

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_object(self):
        queryset = self.get_queryset()
        obj = None
        job_id = self.kwargs.get("pk")

        if ObjectId.is_valid(job_id):
            obj = queryset.filter(_id=ObjectId(job_id)).first()
        else:
            obj = queryset.filter(_id=job_id).first()

        if obj is None:
            raise Http404("Job not found")
        return obj

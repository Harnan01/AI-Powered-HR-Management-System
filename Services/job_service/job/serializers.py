# job/serializers.py
from rest_framework import serializers
from .models import Job
from .fields import ObjectIdField


class JobSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)  # Use ObjectIdField for id

    class Meta:
        model = Job
        fields = '__all__'

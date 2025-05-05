from rest_framework import serializers
from .models import ShortlistingRequest, ShortlistedCandidate

class ShortlistingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortlistingRequest
        fields = '__all__'

class ShortlistedCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortlistedCandidate
        fields = '__all__'

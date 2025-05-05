from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Evaluation
from .serializers import EvaluationSerializer


class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer

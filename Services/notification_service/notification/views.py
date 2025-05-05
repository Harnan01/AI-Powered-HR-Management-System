# notification/views.py
from rest_framework import viewsets
from .models import Notification
from .serializers import NotificationSerializer
from django.core.mail import send_mail
from django.conf import settings


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def perform_create(self, serializer):
        notification = serializer.save()
        send_mail(
            notification.subject,
            notification.message,
            settings.EMAIL_HOST_USER,
            [notification.email],
            fail_silently=False,
        )

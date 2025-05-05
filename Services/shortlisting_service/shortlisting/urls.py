# shortlisting/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShortlistingRequestViewSet

router = DefaultRouter()
router.register(r'shortlisting_requests', ShortlistingRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

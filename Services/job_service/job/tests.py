from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Job
from .serializers import JobSerializer


class JobTests(APITestCase):
    def setUp(self):
        self.job_data = {
            "title": "Software Engineer",
            "description": "We are seeking a talented and motivated Software Engineer to join our dynamic team.",
            "posted_date": "2024-06-16T20:02:52.214498Z",
            "location": "Remote"
        }
        self.job = Job.objects.create(**self.job_data)
        self.valid_payload = {
            "title": "Senior Software Engineer",
            "description": "We are seeking a talented and motivated Senior Software Engineer to join our dynamic team.",
            "posted_date": "2024-06-16T20:02:52.214498Z",
            "location": "Remote"
        }
        self.invalid_payload = {
            "title": "",
            "description": "We are seeking a talented and motivated Senior Software Engineer to join our dynamic team.",
            "posted_date": "2024-06-16T20:02:52.214498Z",
            "location": "Remote"
        }

    def test_create_valid_job(self):
        response = self.client.post(
            reverse('job-list'),
            data=self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_job(self):
        response = self.client.post(
            reverse('job-list'),
            data=self.invalid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_jobs(self):
        response = self.client.get(reverse('job-list'))
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_single_job(self):
        response = self.client.get(reverse('job-detail', kwargs={'pk': self.job.pk}))
        job = Job.objects.get(pk=self.job.pk)
        serializer = JobSerializer(job)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_job(self):
        response = self.client.get(reverse('job-detail', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_valid_job(self):
        response = self.client.put(
            reverse('job-detail', kwargs={'pk': self.job.pk}),
            data=self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_invalid_job(self):
        response = self.client.put(
            reverse('job-detail', kwargs={'pk': self.job.pk}),
            data=self.invalid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_valid_job(self):
        response = self.client.delete(
            reverse('job-detail', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_invalid_job(self):
        response = self.client.delete(
            reverse('job-detail', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

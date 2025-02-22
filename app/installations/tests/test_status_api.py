from unicodedata import name
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status as HTTPstatus
from rest_framework.test import APIClient

from core.models import Status

from installations.serializers import StatusSerializer

STATUS_URL = reverse('installations:status-list')

class PublicStatusApiTests(TestCase):
    """Test the publicly available status API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving statuses"""
        res = self.client.get(STATUS_URL)

        self.assertEqual(res.status_code, HTTPstatus.HTTP_401_UNAUTHORIZED)

class PrivateStatusApiTests(TestCase):
    """Test the authorized user status API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'ryantest@vumatel.com',
            'testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_statuses(self):
        """Test retrieving statuses"""
        Status.objects.create(user=self.user, status='Installation Required')
        Status.objects.create(user=self.user, status='Installation Complete')

        res = self.client.get(STATUS_URL)

        statuses = Status.objects.all().order_by('-status')
        serializer = StatusSerializer(statuses, many=True)

        self.assertEqual(res.status_code, HTTPstatus.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_status_successful(self):
        """Test creating a new status"""
        payload = {'status': 'test_status'}
        self.client.post(STATUS_URL, payload)

        exists = Status.objects.filter(
            user=self.user,
            status=payload['status']
        ).exists()
        self.assertTrue(exists)

    def test_status_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            'other@vumatel.com',
            'testpass'
        )
        Status.objects.create(user=user2, status='Installer')
        status = Status.objects.create(user=self.user, status='Installation Complete')

        res = self.client.get(STATUS_URL)

        self.assertEqual(res.status_code, HTTPstatus.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['status'], status.status)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'status': ''}
        res = self.client.post(STATUS_URL, payload)

        self.assertEqual(res.status_code, HTTPstatus.HTTP_400_BAD_REQUEST)
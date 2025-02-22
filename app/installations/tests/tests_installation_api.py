from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status as HTTPstatus

from core.models import Installation

import datetime

from installations.serializers import InstallationSerializer

INSTALLATION_URL = reverse('installations:installations-list')

def sample_installation(user, **params):
    """Create and return a sample installation"""
    defaults = {
        'customer_name': 'Phillip Moss',
        'address': '17 Petunia Street',
        'apointment_date': datetime.date(2022, 10, 22)
    }
    defaults.update(params)

    return Installation.objects.create(user=user, **defaults)


class PublicInstallationApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(INSTALLATION_URL)

        self.assertEqual(res.status_code, HTTPstatus.HTTP_401_UNAUTHORIZED)


class PrivateInstallationApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'ryantest@vumatel.co.za',
            'testpass'
        )
        self.user.force_authenticate(self.user)

    def test_retrieve_installations(self):
        """Test retrieving a list of installations"""
        sample_installation(user=self.user)
        sample_installation(user=self.user)

        res = self.client.get(INSTALLATION_URL)

        installations = Installation.objects.all().order_by('-id')
        serializer = InstallationSerializer(installations, many=True)
        self.assertEqual(res.status_code, HTTPstatus.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_installation_limited_to_user(self):
        """Test retrieving installations for user"""
        user2 = get_user_model().objects.create_user(
            'ryantest@vumatel.co.za',
            'password123'
        )
        sample_installation(user=user2)
        sample_installation(user=self.user)

        res = self.client.get(INSTALLATION_URL)

        installations = Installation.objects.filter(user=self.user)
        # List installation api returns list
        serializer = InstallationSerializer(installations, many=True)

        self.assertEqual(res.status_code, HTTPstatus.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

from django.test import TestCase
from authentication.models import LibraryUser, MemberProfile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


class LibraryUserTest(TestCase):

    def test_create_admin_user(self):
        admin_user = LibraryUser.objects.create_user(
            username='admin_user',
            password='adminpass123',
            role='admin'
        )
        self.assertEqual(admin_user.role, 'admin')
        self.assertTrue(admin_user.is_admin)

    def test_create_librarian_user(self):
        librarian_user = LibraryUser.objects.create_user(
            username='librarian_user',
            password='librarianpass123',
            role='librarian'
        )
        self.assertEqual(librarian_user.role, 'librarian')
        self.assertTrue(librarian_user.is_librarian)

    def test_create_member_user(self):
        member_user = LibraryUser.objects.create_user(
            username='member_user',
            password='memberpass123',
            role='member'
        )
        self.assertEqual(member_user.role, 'member')
        self.assertTrue(member_user.is_member)


class MemberProfileTest(TestCase):

    def setUp(self):
        self.member_user = LibraryUser.objects.create_user(
            username='member_user',
            password='memberpass123',
            role='member'
        )

    def test_create_member_profile(self):
        profile = MemberProfile.objects.create(user=self.member_user)
        self.assertEqual(profile.user.username, 'member_user')
        self.assertIsNotNone(profile.membership_date)


class LibraryUserInvalidTest(TestCase):

    def test_create_user_without_role(self):
        user = LibraryUser.objects.create_user(
            username='invalid_user',
            password='invalidpass123'
        )
        self.assertEqual(user.role, 'member')


class LibraryUserContactTest(TestCase):

    def test_create_user_with_contact(self):
        user = LibraryUser.objects.create_user(
            username='contact_user',
            password='contactpass123',
            role='member',
            contact_number='1234567890',
            address='123 Library St.'
        )
        self.assertEqual(user.contact_number, '1234567890')
        self.assertEqual(user.address, '123 Library St.')


User = get_user_model()


class AuthenticationTests(APITestCase):

    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'testuser@example.com',
            'phone_number': '09143456789',
            'role': 'member'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_user_with_existing_username(self):
        User.objects.create_user(username='testuser', password='testpassword', contact_number='09123456789')
        url = reverse('register')
        data = {
            'username': 'testuser',
            'password': 'newpassword',
            'email': 'newuser@example.com',
            'phone_number': '09123456790',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class AuthenticationLoginTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', contact_number='09143456789')

    def test_login_user(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_invalid_credentials(self):
        url = reverse('login')
        data = {
            'username': 'wronguser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticationLogoutTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', contact_number='09123456789')
        self.refresh = RefreshToken.for_user(self.user)

    def test_logout_user(self):
        url = reverse('logout')
        data = {
            "refresh": str(self.refresh)
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_with_invalid_token(self):
        url = reverse('logout')
        data = {
            'refresh': 'invalidtoken'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProtectedViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', contact_number='09123456789')
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_access_protected_view_with_token(self):
        url = reverse('protected')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'this is a protected API')

    def test_access_protected_view_without_token(self):
        url = reverse('protected')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RefreshTokenTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', contact_number='09143456789')
        self.refresh = RefreshToken.for_user(self.user)
        self.url = reverse('token_refresh')

    def test_refresh_token(self):
        response = self.client.post(self.url, {'refresh': str(self.refresh)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('access', response.data)

    def test_invalid_refresh_token(self):
        response = self.client.post(self.url, {'refresh': 'invalid_refresh_token'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

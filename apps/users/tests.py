from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserRegistrationTests(TestCase):
    """
    Tests for the registration endpoint: password confirmation,
    email uniqueness, and correct password hashing.

    Тесты эндпоинта регистрации: подтверждение пароля, уникальность
    email, корректное хеширование пароля.
    """

    def setUp(self):
        self.client = APIClient()

    def test_successful_registration(self):
        """A valid registration request should create a new user."""
        response = self.client.post('/api/users/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123',
            'password_confirm': 'StrongPass123',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_password_mismatch_is_rejected(self):
        """Registration should fail if password and password_confirm differ."""
        response = self.client.post('/api/users/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123',
            'password_confirm': 'DifferentPass456',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_is_rejected(self):
        """Registration should fail if the email is already in use."""
        User.objects.create_user(
            username='existing', email='taken@example.com', password='pass12345',
            address='Test address',
        )
        response = self.client.post('/api/users/register/', {
            'username': 'newuser',
            'email': 'taken@example.com',
            'password': 'StrongPass123',
            'password_confirm': 'StrongPass123',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_hashed_not_stored_as_plain_text(self):
        """The stored password must be a hash, not the raw input."""
        self.client.post('/api/users/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123',
            'password_confirm': 'StrongPass123',
        })
        user = User.objects.get(email='newuser@example.com')
        self.assertNotEqual(user.password, 'StrongPass123')
        self.assertTrue(user.check_password('StrongPass123'))


class UserLoginTests(TestCase):
    """
    Tests for JWT login, which authenticates by email (USERNAME_FIELD),
    not by username.

    Тесты JWT-логина, который аутентифицирует по email
    (USERNAME_FIELD), а не по username.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='loginuser', email='login@example.com', password='pass12345',
            address='Test address',
        )

    def test_login_with_correct_email_and_password(self):
        """Logging in with the correct email/password should return tokens."""
        response = self.client.post('/api/users/login/', {
            'email': 'login@example.com',
            'password': 'pass12345',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_wrong_password_is_rejected(self):
        """Logging in with an incorrect password should fail."""
        response = self.client.post('/api/users/login/', {
            'email': 'login@example.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_user_cannot_login(self):
        """A soft-deleted (is_active=False) user should not be able to log in."""
        self.user.is_active = False
        self.user.save()
        response = self.client.post('/api/users/login/', {
            'email': 'login@example.com',
            'password': 'pass12345',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTests(TestCase):
    """
    Tests for the authenticated user's own profile endpoint.

    Тесты эндпоинта собственного профиля авторизованного пользователя.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='profileuser', email='profile@example.com', password='pass12345',
            address='Test address',
        )

    def test_unauthenticated_user_cannot_access_profile(self):
        """Anonymous users should not be able to view /users/me/."""
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_view_own_profile(self):
        """An authenticated user should see their own profile data."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profile@example.com')

    def test_user_can_update_own_profile(self):
        """An authenticated user should be able to update their own bio."""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch('/api/users/me/', {
            'bio': 'Updated bio text',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, 'Updated bio text')

    def test_username_cannot_be_changed_via_profile(self):
        """username is read-only on the profile endpoint and should
        not change even if submitted in the request."""
        self.client.force_authenticate(user=self.user)
        self.client.patch('/api/users/me/', {'username': 'hacked'})
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'profileuser')


class UserSoftDeleteTests(TestCase):
    """
    Tests for the soft-delete behavior on the User model.

    Тесты поведения мягкого удаления модели User.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='deleteuser', email='delete@example.com', password='pass12345',
            address='Test address',
        )

    def test_delete_deactivates_instead_of_removing(self):
        """Calling delete() should set is_active=False, not remove the row."""
        user_id = self.user.id
        self.user.delete()

        self.assertTrue(User.objects.filter(id=user_id).exists())
        deactivated = User.objects.get(id=user_id)
        self.assertFalse(deactivated.is_active)

    def test_hard_delete_actually_removes_the_row(self):
        """hard_delete() should permanently remove the user."""
        user_id = self.user.id
        self.user.hard_delete()
        self.assertFalse(User.objects.filter(id=user_id).exists())
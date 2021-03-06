from django.utils.http import urlsafe_base64_encode
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.utils.encoding import force_bytes
from authors.apps.authentication.tests import BaseTest
from authors.apps.authentication.models import User


class AuthenticationTests(BaseTest):

    def test_username_label(self):
        field_label = self.user._meta.get_field('username').verbose_name
        self.assertEquals(field_label, 'username')

    def test_get_full_name(self):
        self.assertEquals("user_test", self.user.get_full_name)

    def test_get_short_name(self):
        self.assertEquals("user_test", self.user.get_short_name())

    def test_user_str_representation(self):
        self.assertEqual(self.user.__str__(), "mail@me.com")

    def test_user_registration(self):
        self.assertEqual(self.register_response.status_code, status.HTTP_201_CREATED)

    def test_user_account_activation(self):
        user = get_object_or_404(User, email=self.register_response.data["email"])
        user_id = urlsafe_base64_encode(force_bytes(user.id)).decode()
        token = self.register_response.data["token"]
        response = self.client.get("/api/activate/"+user_id+"/"+token+"/account/", format="json")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_account_activation_with_wrong_values(self):
        response = self.client.get("/api/activate/wq/jskjahjs/account/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_update(self):
        """Test if a user can update his username"""
        response = self.client.put("/api/user/", self.user_validate_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_login_with_email(self):
        self.assertEqual(self.login_response.status_code, status.HTTP_200_OK)

    def test_user_login_without_email_and_password(self):
        response = self.client.post("/api/users/login/",
                                    {"user": {}}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_invalid_credentials(self):
        response = self.client.post("/api/users/login/", self.unregistered_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_response_on_register(self):
        response = self.register_response
        self.assertEqual(len(response.data["token"]) > 2, True)

    def test_no_token_provided(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="invalid token")
        response = self.client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_retrieve(self):
        response = self.client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_request_password_reset(self):
        response = self.client.post('/api/password-reset/', {"email": "mail@me.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_request_password_reset_with_an_unregistered_email(self):
        response = self.client.post('/api/password-reset/', {"email": "uregistered@invalid.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_redirect_to_password_reset(self):
        self.client.post('/api/password-reset/', {"email": "mail@me.com"}, format="json")
        response = self.client.get('/api/password-reset/<str:token>/', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_new_password_reset_done(self):
        data = {"user": {"password": "23newpassword"}}

        self.client.post('/api/password-reset/', {"email": "mail@me.com"}, format="json")
        self.client.get('/api/password-reset/<str:token>/', format="json")
        response = self.client.put('/api/password-reset/done/', data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_new_password_reset_done_with_a_weak_password(self):
        data = {"user": {"password": "1"}}
        self.client.post('/api/password-reset/', {"email": "mail@me.com"}, format="json")
        self.client.get('/api/password-reset/<str:token>/', format="json")
        response = self.client.put('/api/password-reset/done/', data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



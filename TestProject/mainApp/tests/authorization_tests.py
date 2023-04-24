from rest_framework import status
from rest_framework.test import APITestCase

from mainApp.models import User


class AuthorizationTests(APITestCase):
    def setUp(self):
        self.user1, create = User.objects.get_or_create(username='test user', phone_number='88005553577')

    def test_registration(self):
        data = {'phone_number': '89001234545'}
        response = self.client.post("/authorize/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertFalse(data['send_otp'])
        self.assertTrue(data['need_reg'])

        data = {'phone_number': '89001234545', 'username': 'new user'}
        response = self.client.put("/authorize/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['send_otp'])
        self.assertFalse(data['need_reg'])

        user = User.objects.get(phone_number=89001234545)
        self.assertEqual(user.username, 'new user')

        data = {'phone_number': '89001234545', 'otp': '777'}
        response = self.client.post("/confirmAuthorization/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['id'], 2)

    def test_authorization(self):
        data = {'phone_number': '88005553577'}
        response = self.client.post("/authorize/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['send_otp'])
        self.assertFalse(data['need_reg'])

        data = {'phone_number': '88005553577', 'otp': '777'}
        response = self.client.post("/confirmAuthorization/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['id'], 1)

    def test_get_user_info(self):
        response = self.client.get("/user/", format='json', headers={'token': self.user1.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data[0]['id'], 1)

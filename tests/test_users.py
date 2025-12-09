from app import create_app
from app.models import Users, db
from werkzeug.security import check_password_hash, generate_password_hash
import unittest
from app.utils.util import encode_token

class TestUser(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.user = Users(email="tester@email.com", username="tester", password=generate_password_hash('123'), role='user') #Creating a starter user, to test things like get, login, update, and delete
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.user)
            db.session.commit()
        self.token = encode_token(1) #encoding a token for my starter User defined above ^
        self.client = self.app.test_client()
        
    def test_create_user(self):
        user_payload = {
            "email": "test@email.com",
            "username": "test_user",
            "password": "123",
            "role": "admin",
            "DOB": "1900-01-01",
            "address": "123 Fun St."
        }
        
        response = self.client.post("/users", json=user_payload) # sending a test POST request using our test_client, and including the JSON body
        print(response.json)
        self.assertEqual(response.status_code, 201) # checking if we got a 201 status code back from creating a user
        self.assertEqual(response.json['username'], 'test_user') # checking to make sure the username is equal to test_user, as it is set in the testcase
        self.assertTrue(check_password_hash(response.json['password'], "123"))

    def test_invalid_user(self):
        user_payload = { # Missing the email field, it is required
            "username": "test_user",
            "password": "123",
            "role": "admin",
            "DOB": "1900-01-01",
            "address": "123 Fun St."
        }
        
        response = self.client.post("/users", json=user_payload)
        self.assertEqual(response.status_code, 400) 
        self.assertIn('email', response.json) #Membership check that email is in the response json

    def test_login(self):
        login_creds = {
            "username": "tester",
            "password": "123"
        }
        
        response = self.client.post('/users/login', json=login_creds)
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_token', response.json)
        
    def test_get_users(self):
        
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['username'], 'tester')
        
    def test_non_unique_email(self):
        user_payload = {
            "email": "tester@email.com",
            "username": "test_user",
            "password": "123",
            "role": "admin",
            "DOB": "1900-01-01",
            "address": "123 Fun St."
        }
        
        response = self.client.post('/users', json=user_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'email is taken')
        
    def test_delete(self):
        headers = {'Authorization': "Bearer " + self.token}
        
        response = self.client.delete('/users', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully deleted user 1')
        
    def test_unauthorized_delete(self):
        
        response = self.client.delete('/users')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], 'Token is missing!!')
        
    def test_update(self):
        headers = {"Authorization": "Bearer " + self.token}

        update_payload = {
            "email": "NEW_EMAIL@email.com",
            "username": "test_user5",
            "password": "123",
            "role": "admin",
            "DOB": "1900-01-01",
            "address": "123 Fun St."
        }

        response = self.client.put('/users', headers=headers, json=update_payload)
        print(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], 'NEW_EMAIL@email.com')
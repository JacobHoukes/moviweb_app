import unittest
from app import app

class MovieWebAppTestCase(unittest.TestCase):
    def setUp(self):
        # Set up test client
        self.client = app.test_client()
        self.client.testing = True

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_users_route(self):
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Users', response.data)

    def test_404_error(self):
        response = self.client.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Page Not Found', response.data)

if __name__ == '__main__':
    unittest.main()

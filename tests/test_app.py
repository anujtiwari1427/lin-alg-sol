"""
Unit Tests — Linear Algebra Solver Comprehensive Test Suite
Run with: python -m unittest discover tests
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from config import Config


class TestRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_fd, cls.db_path = tempfile.mkstemp(suffix='.db')
        class RouteConfig(Config):
            TESTING = True
            DEBUG = False
            DATABASE_PATH = cls.db_path

        cls.app = create_app(RouteConfig)
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        os.close(cls.db_fd)
        if os.path.exists(cls.db_path):
            os.unlink(cls.db_path)

    def test_landing_page_ok(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Linear Algebra Solver', r.data)

    def test_dashboard_page_ok(self):
        r = self.client.get('/dashboard')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Workspace Dashboard', r.data)

    def test_health_endpoint_ok(self):
        r = self.client.get('/health')
        self.assertEqual(r.status_code, 200)
        payload = json.loads(r.data)
        self.assertEqual(payload['status'], 'healthy')

    def test_matrix_route_ok(self):
        r = self.client.get('/matrix')
        self.assertEqual(r.status_code, 200)

    def test_determinant_route_ok(self):
        r = self.client.get('/determinant')
        self.assertEqual(r.status_code, 200)

    def test_inverse_route_ok(self):
        r = self.client.get('/inverse')
        self.assertEqual(r.status_code, 200)

    def test_vector_route_ok(self):
        r = self.client.get('/vector')
        self.assertEqual(r.status_code, 200)

    def test_linear_equations_route_ok(self):
        r = self.client.get('/linear-equations')
        self.assertEqual(r.status_code, 200)

    def test_eigen_route_ok(self):
        r = self.client.get('/eigen')
        self.assertEqual(r.status_code, 200)

    def test_404_handler(self):
        r = self.client.get('/nonexistent-page-xyz')
        self.assertEqual(r.status_code, 404)


class TestCalculationAPIs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_fd, cls.db_path = tempfile.mkstemp(suffix='.db')
        class ApiConfig(Config):
            TESTING = True
            DEBUG = False
            DATABASE_PATH = cls.db_path

        cls.app = create_app(ApiConfig)
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        os.close(cls.db_fd)
        if os.path.exists(cls.db_path):
            os.unlink(cls.db_path)

    def test_matrix_addition(self):
        r = self.client.post('/api/matrix/calculate', json={
            'operation': 'add',
            'matrix_a': [[1, 2], [3, 4]],
            'matrix_b': [[5, 6], [7, 8]]
        })
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['result'], [[6.0, 8.0], [10.0, 12.0]])

    def test_matrix_multiplication(self):
        r = self.client.post('/api/matrix/calculate', json={
            'operation': 'multiply',
            'matrix_a': [[1, 2], [3, 4]],
            'matrix_b': [[2, 0], [1, 2]]
        })
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['result'], [[4.0, 4.0], [10.0, 8.0]])

    def test_determinant_api(self):
        r = self.client.post('/api/determinant/calculate', json={
            'matrix': [[4, 2], [1, 3]]
        })
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['result'], 10.0)

    def test_inverse_api(self):
        r = self.client.post('/api/inverse/calculate', json={
            'matrix': [[4, 7], [2, 6]]
        })
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data['success'])
        self.assertIn('result', data)

    def test_vector_dot_api(self):
        r = self.client.post('/api/vector/calculate', json={
            'operation': 'dot',
            'vector_a': [1, 2, 3],
            'vector_b': [4, 5, 6]
        })
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['result'], 32.0)

    def test_linear_equations_gaussian_api(self):
        r = self.client.post('/api/linear-equations/calculate', json={
            'method': 'gaussian',
            'coefficients': [[2, 1], [1, -1]],
            'constants': [8, 1]
        })
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['solution'], {'x1': '3', 'x2': '2'})

    def test_eigen_api(self):
        r = self.client.post('/api/eigen/calculate', json={
            'matrix': [[4, 2], [1, 3]]
        })
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['eigenvalues']), 2)


if __name__ == '__main__':
    unittest.main()

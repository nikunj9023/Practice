import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as app_module


class ErpApiTests(unittest.TestCase):
    def setUp(self):
        app_module.app.config['TESTING'] = True
        app_module.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app_module.app.test_client()
        with app_module.app.app_context():
            app_module.db.drop_all()
            app_module.db.create_all()

    def get_token(self):
        resp = self.client.post('/api/login', json={'username': 'admin', 'password': 'password'})
        self.assertEqual(resp.status_code, 200)
        return resp.get_json()['token']

    def test_tenant_and_module_endpoints(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}

        resp = self.client.post('/api/tenants', json={'name': 'Acme', 'slug': 'acme'}, headers=headers)
        self.assertEqual(resp.status_code, 201)
        tenant = resp.get_json()['tenant']

        resp = self.client.post('/api/customers', json={'tenant_id': tenant['id'], 'name': 'Jane Doe', 'email': 'jane@example.com'}, headers=headers)
        self.assertEqual(resp.status_code, 201)

        resp = self.client.get(f"/api/customers?tenant_id={tenant['id']}", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()['items']), 1)

        resp = self.client.post('/api/invoices', json={'tenant_id': tenant['id'], 'invoice_number': 'INV-001', 'customer_id': 1, 'amount': 1250.5}, headers=headers)
        self.assertEqual(resp.status_code, 201)

        invoices = self.client.get(f"/api/invoices?tenant_id={tenant['id']}", headers=headers).get_json()['items']
        self.assertEqual(len(invoices), 1)


if __name__ == '__main__':
    unittest.main()

"""HTTP contract regressions without connecting to vendor data or Redis."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from flask import Flask, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash
import time

SOURCE = Path(__file__).resolve().parents[1] / 'routes/auth_routes.py'


class LoginTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(SOURCE.read_text())
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('login_route','_verify_password')]
        for fn in functions: fn.decorator_list=[]
        self.account = Mock()
        self.account.query.filter.return_value.first.return_value = SimpleNamespace(id=1)
        self.passwords = Mock()
        self.passwords.query.join.return_value.filter.return_value.with_entities.return_value.first.return_value = SimpleNamespace(password=generate_password_hash('correct-password'), must_change_password=False)
        self.vendor = Mock()
        self.ensure = Mock()
        scope=dict(request=request,jsonify=jsonify,current_app=current_app,time=time,
                   _ensure_password_force_change_column=self.ensure, VendorAccount=self.account,
                   PasswordManager=self.passwords, Vendor=self.vendor, Console=Mock(),func=Mock(),and_=Mock(),
                   check_password_hash=check_password_hash)
        exec(compile(ast.Module(body=functions,type_ignores=[]),str(SOURCE),'exec'),scope)
        app=Flask(__name__)
        app.add_url_rule('/api/login',view_func=scope['login_route'],methods=['POST'])
        self.client=app.test_client()

    def test_missing_password_is_400_before_database_access(self):
        result=self.client.post('/api/login',json={'email':'vendor@example.com','parent_type':'vendor'})
        self.assertEqual(result.status_code,400)
        self.assertNotIn('vendors',result.json)
        self.ensure.assert_not_called()
        self.account.query.filter.assert_not_called()

    def test_wrong_password_is_401_and_does_not_list_vendors(self):
        result=self.client.post('/api/login',json={'email':'vendor@example.com','parent_type':'vendor','password':'wrong'})
        self.assertEqual(result.status_code,401)
        self.assertNotIn('vendors',result.json)
        self.vendor.query.outerjoin.assert_not_called()

    def test_unknown_account_returns_401(self):
        self.account.query.filter.return_value.first.return_value=None
        result=self.client.post('/api/login',json={'email':'unknown@example.com','parent_type':'vendor','password':'test'})
        self.assertEqual(result.status_code,401)
        self.assertNotIn('vendors',result.json)

    def test_correct_password_returns_vendor_list(self):
        self.vendor.query.outerjoin.return_value.filter.return_value.with_entities.return_value.group_by.return_value.all.return_value = [SimpleNamespace(id=1,cafe_name='Test',owner_name='Owner',description='',pc_count=2)]
        result=self.client.post('/api/login',json={'email':'vendor@example.com','parent_type':'vendor','password':'correct-password'})
        self.assertEqual(result.status_code,200,result.json)
        self.assertEqual(result.json['vendors'][0]['pc_count'],2)


if __name__=='__main__': unittest.main()

# -*- coding: utf-8 -*-
"""import depancies."""
import unittest

from flask import current_app
from flask_testing import TestCase

from app import app
from config import APP_CONFIG


class TestDevelopmentConfig(TestCase):
    """Test App is in Development"""
    def create_app(self):
        app.config.from_object(APP_CONFIG['development'])
        return app

    def test_app_is_development(self):
        """Test App is running DEBUG in Development"""

        self.assertTrue(app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)


class TestProductionConfig(TestCase):
    """Test App is in Development"""
    def create_app(self):
        app.config.from_object(APP_CONFIG['production'])
        return app

    def test_app_is_production(self):
        """Test App is running DEBUG in Production"""
        self.assertTrue(app.config['DEBUG'] is False)


if __name__ == '__main__':
    unittest.main()
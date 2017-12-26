"""import depancies."""
import os

class Config(object):
    """
    Common configurations
    """

    DEBUG = False


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False


APP_CONFIG = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing':TestingConfig
}

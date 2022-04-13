from .base import Base


class External(Base):
    DEBUG = True
    ALLOWED_HOSTS = ['*']
    CSRF_TRUSTED_ORIGINS = [
        'http://127.0.0.1:8000',
        'http://localhost:8000',
    ]

    STATIC_URL = "staticfiles/"

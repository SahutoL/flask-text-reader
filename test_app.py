import pytest
from app import create_app
from config import Config

class TestConfig(Config):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
    SECRET_KEY = "test_secret_key"
    DEBUG = True

@pytest.fixture
def app():
    app = create_app(TestConfig)
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'テキストリーダーへようこそ' in response.data.decode('utf-8')

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert 'ログイン' in response.data.decode('utf-8')

def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert 'ユーザー登録' in response.data.decode('utf-8')

import random
import string

import pytest
from rest_framework.test import APIClient

from app.test.api_client import DRFClient

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def user(mixer):
    user = mixer.blend('a12n.User', is_superuser=False)
    user.set_password('password')
    user.save()
    return user


@pytest.fixture
def api():
    return DRFClient(anon=True)


@pytest.fixture
def get_token(api):
    return lambda email: api.post('/api/v1/auth/token/', {
        'email': email,
        'password': 'password',
    }, format='json', as_response=True)


def test_getting_token_ok(user, get_token, api):
    got = get_token(user.email)
    assert got.status_code == 200


def test_getting_tokens_is_token(api, user, get_token):
    got = get_token(user.email)

    got = api._decode(got)
    assert len(got['access']) > 32  # i thing that every stuff that is long enough, can be a JWT token
    assert len(got['refresh']) > 32
    assert len(got['access'].split('.')) == 3
    assert len(got['refresh'].split('.')) == 3


@pytest.mark.parametrize('header', [
    'JWT',
    'Bearer'
])
def test_received_access_token_works(api, user, get_token, header):
    """Try to check valid token"""
    got = api._decode(get_token(user.email))

    token = got['access']

    c = APIClient()  # we use vanilla DRF test client to ensure it has no 'convenience' modifications from the test case
    c.credentials(HTTP_AUTHORIZATION=f'{header} {token}')

    got = c.get('/api/v1/whoami/')
    assert got.status_code == 200

    got = api._decode(got)
    assert got['id'] == user.id


@pytest.mark.parametrize('header', [
    'JWT',
    'Bearer'
])
def test_invalid_access_token_does_not_work(header):
    token = ''.join([random.choice(string.hexdigits) for _ in range(0, 32)])

    c = APIClient()  # we use vanilla DRF test client to ensure it has no 'convenience' modifications from the test case
    c.credentials(HTTP_AUTHORIZATION=f'{header} {token}')

    got = c.get('/api/v1/whoami/')
    assert got.status_code == 401


def test_refresh_access_token(api, user, get_token):
    got = api._decode(get_token(user.email))

    access_token = got['access']
    refresh_token = got['refresh']

    c = APIClient()  # we use vanilla DRF test client to ensure it has no 'convenience' modifications from the test case

    got = c.post('/api/v1/auth/token/refresh/', {'refresh': refresh_token})
    assert got.status_code == 200

    got = api._decode(got)
    assert len(got['access']) > 32
    assert len(got['refresh']) > 32
    assert len(got['refresh']) != refresh_token
    assert len(got['access']) != access_token

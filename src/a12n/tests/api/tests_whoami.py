import pytest

from app.test.api_client import DRFClient

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def user(mixer):
    user = mixer.blend('a12n.User', is_superuser=False)
    return user


@pytest.fixture
def api(user):
    return DRFClient(user=user, god_mode=False)


def test_login_is_required(api):
    api.logout()

    response = api.get('/api/v1/whoami/', as_response=True)

    assert response.status_code == 401


def test_has_required_fields(user, api):
    got = api.get('/api/v1/whoami/')

    assert got['username'] == user.username
    assert got['email'] == user.email

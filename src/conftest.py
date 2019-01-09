import sys
from datetime import datetime as stock_datetime
from unittest.mock import MagicMock

import pytest
import pytz
import simplejson
from django.utils import timezone, translation
from faker import Faker

from app.test import mixer as _mixer
from app.test import redis
from app.test.api_client import DRFClient


def pytest_load_initial_conftests(args):
    if "xdist" in sys.modules:  # pytest-xdist plugin
        import multiprocessing

        num = max(multiprocessing.cpu_count() / 2, 1)
        args[:] = ["-n", str(num)] + args


@pytest.fixture(autouse=True)
def redis_transaction(settings):
    """Flush all redis data on every test teardown, to avoid celery-once glitches and other weird test interference during parallel runs"""
    yield
    redis.flush_all()


@pytest.fixture(autouse=True)
def set_redis_connection_based_on_xdist_thread(worker_id, settings):
    """Make all test threads work with different redis connections. Worker_id comes from pytest-xdist"""
    db = redis.get_redis_db_num(worker_id)

    settings.CACHES['default']['LOCATION'] = redis.replace_db_num(settings.CACHES['default']['LOCATION'], db)
    settings.CELERY_ONCE['settings']['url'] = redis.replace_db_num(settings.CELERY_ONCE['settings']['url'], db)


@pytest.fixture
def mixer():
    return _mixer


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture
def api(db):
    return DRFClient()


@pytest.fixture
def connect_mock_handler():
    def _connect_mock_handler(signal):
        handler = MagicMock()
        signal.connect(handler)
        return handler

    return _connect_mock_handler


@pytest.fixture
def read_fixture():
    """Fixture reader"""
    def read_file(fname):
        with open(fname) as fp:
            return simplejson.load(fp)

    return read_file


@pytest.fixture
def _datetime(settings):
    """Create a timezoned datetime"""
    def _f(*args, **kwargs):
        if isinstance(args[0], int):
            tz = settings.TIME_ZONE
        else:
            tz = args[0]
            args = args[1:]

        tz = pytz.timezone(tz)
        return timezone.make_aware(
            stock_datetime(*args, **kwargs),
            timezone=tz,
        )

    return _f


@pytest.fixture
def ru():
    with translation.override('ru'):
        yield


@pytest.fixture
def en():
    with translation.override('en'):
        yield


@pytest.fixture(autouse=True, scope='function')
def password_hashers(settings):
    """Forces django to use fast password hashers for tests."""
    settings.PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]

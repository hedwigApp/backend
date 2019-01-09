import pytest

from app.test import redis


@pytest.fixture(autouse=True)
def freeze_min_redis_db_num(monkeypatch):
    monkeypatch.setattr(redis, 'MIN_REDIS_DB_NUM', 5)


@pytest.mark.parametrize('worker_id, expected', [
    ['master', 5],
    ['gw0', 7],
    ['gw1', 8],
    ['fuck', 6],
])
def test_db_num(worker_id, expected):
    assert redis.get_redis_db_num(worker_id) == expected


@pytest.mark.parametrize('inpt, expected', [
    ['redis://127.0.0.1:5432/5', 'redis://127.0.0.1:5432/100500'],
    ['redis://127.0.0.1:5432/50', 'redis://127.0.0.1:5432/100500'],
    ['redis://127.0.0.1:5432/', 'redis://127.0.0.1:5432/100500'],
])
def test_replacing_db_num(inpt, expected):
    assert redis.replace_db_num(inpt, 100500) == expected

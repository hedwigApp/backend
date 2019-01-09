"""Various helpers for redis testing"""
import re

from django_redis import get_redis_connection

MIN_REDIS_DB_NUM = 3


def flush_all():
    get_redis_connection('default').flushall()


def get_redis_db_num(worker_id) -> int:
    """Attempt to guess unique redis DB num for each test worker thread"""
    if worker_id == 'master':
        return MIN_REDIS_DB_NUM

    worker_id_digits = ''.join(char for char in worker_id if char.isdigit())

    worker_id_digits = int(worker_id_digits) + 1 if len(worker_id_digits) else 0

    return MIN_REDIS_DB_NUM + 1 + worker_id_digits


def replace_db_num(connection_string, db) -> str:
    return re.sub(r'/(\d*)\Z', f'/{db}', connection_string)

from abc import ABC, abstractmethod
import redis
import os

from celery import Celery


REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_PASS = os.environ.get('REDIS_PASS', None)


if REDIS_PASS:
    app = Celery(
        'compositor',
        broker=f'redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}/0',
        backend=f'redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}/0',
    )
else:
    app = Celery(
        'compositor',
        broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/0',
        backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
    )
app.autodiscover_tasks(['libs.tasks'])
app.conf.timezone = 'Europe/Moscow'
# app.conf.update(result_expires=3600)


class StorageInterface(ABC):
    @abstractmethod
    def enqueue(self, key, message):
        pass

    @abstractmethod
    def dequeue(self, key, queue_name):
        pass

    @abstractmethod
    def read(self, key, start=0, stop=-1):
        pass

    @abstractmethod
    def remove(self, key):
        pass

    @abstractmethod
    def __enter__(self, host):
        pass

    @abstractmethod
    def __exit__(self):
        pass


class Redis(StorageInterface):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, db=0):

        if password:
            self.redis_client = redis.StrictRedis(host=host, port=port, password=password)
        else:
            self.redis_client = redis.Redis(host=host, port=port, db=db)

    def enqueue(self, key: str, message: dict) -> None:
        self.redis_client.rpush(key, message)

    def dequeue(self, key: str) -> str:
        return self.redis_client.lpop(key)

    def read(self, key: str, start=0, stop=-1):
        items = self.redis_client.lrange(key, start, stop)
        return items

    def remove(self, key):
        self.redis_client.lrem(key, 0, -1)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        pass


class Queue(Redis):
    pass

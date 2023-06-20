import redis

from OJ.app.settings import *
from OJ.util.constant import *


class Cache(object):
    def __init__(self, queue=CacheKey.waiting_queue, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD,
                 db=REDIS_DB):
        self.queue_name = queue
        self.client = redis.Redis(host=host, port=port, password=password, db=db)

    def push(self, data):
        self.client.rpush(self.queue_name, data)

    def pop(self):
        return self.client.lpop(self.queue_name)

    def __getitem__(self, ix):
        return self.client.lindex(self.queue_name, ix)

    def __len__(self):
        return self.client.llen(self.queue_name)

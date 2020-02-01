import redis
from deep_sort_pytorch.RLogger import RLogger
import yaml

config_path='deep_sort_pytorch/configs/redis_config.yml'
with open(config_path, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
    redis_init = cfg['redis_init']
    host = redis_init[0]
    port = redis_init[1]
    password = redis_init[2]

r = redis.StrictRedis(host=host, port=port, db=0, charset="utf-8", decode_responses=True, password=password)
rlogger = RLogger(r=r)

r.flushdb()
#rlogger.record_tracked_object(video_id=0, time_start=1234123422, time_end=21341234123412310, rectangle_l=[[1,4], [1,2]], class_id='human')

keys = r.keys('*')

for key in keys:
    print('KEY', key)

    type = r.type(key)
    if type == "string":
        val = r.get(key)
    if type == "hash":
        vals = r.hgetall(key)
    if type == "zset":
        vals = r.zrange(key, 0, -1)
    if type == "list":
        vals = r.lrange(key, 0, -1)
    if type == "set":
        vals = r.smembers(key)
    print(vals)

#print(len(r.zrangebyscore('events', 10, 100000100000, withscores=True)))

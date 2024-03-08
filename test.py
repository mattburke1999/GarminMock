import redis
import os
from dotenv import load_dotenv
import uuid
import json
load_dotenv(override=True)

redis_cnxn = redis.Redis(host='localhost', port=6379, db=0, password = os.environ.get('redis_password'))

def create_cookie(value, expire=3600):
    # Generate a unique key for the cookie
    cookie_key = str(uuid.uuid4())
    # Store the value in Redis with an expiration time
    redis_cnxn.setex(cookie_key, expire, value)
    # Return the unique key
    return cookie_key

def get_cookie_value(id):
    # Atomically get and delete the value from Redis
    value = redis_cnxn.get(id)
    if value:
        print('got value from redis')
        # self.redis_cnxn.delete(id)
        # Convert bytes to string if necessary
        return value.decode('utf-8')
    print('no value from redis')
    return None
# test if connection is working
# print(os.environ.get('redis_password'))
list1 = [1,2,3,4,5]
key = create_cookie(json.dumps(list1))
value = json.loads(get_cookie_value(key))
print(value)
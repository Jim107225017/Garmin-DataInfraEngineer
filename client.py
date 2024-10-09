import asyncio
import random
import string

import aioredis_cluster

IOPS = 10000

def random_string(length=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

async def generate_random_data(redis):
    data_type = random.choice(["string", "hash", "list", "set", "zset"])
    key = f"{data_type}:{random_string(5)}"
    
    if data_type == "string":
        value = random_string(20)
        await redis.set(key, value)
    
    elif data_type == "hash":
        for i in range(5):
            await redis.hset(key, f"field_{i}", random_string(8))
    
    elif data_type == "list":
        value = [random_string(6) for _ in range(10)]
        await redis.rpush(key, *value)
    
    elif data_type == "set":
        value = {random_string(6) for _ in range(10)}
        await redis.sadd(key, *value)
    
    elif data_type == "zset":
        for _ in range(10):
            await redis.zadd(key, random.uniform(0, 100), random_string(6))

async def run_tasks(redis):
    while True:
        tasks = [generate_random_data(redis) for _ in range(IOPS)]
        await asyncio.gather(*tasks)
        print(f"Completed {IOPS} operations.")
        
        await asyncio.sleep(1)

async def main():
    # Connection Pool
    redis = await aioredis_cluster.create_redis_cluster([
        "redis://redis-node-1",
    ], pool_minsize=5, pool_maxsize=50, max_attempts=0)
    
    await run_tasks(redis)
    
    # Graceful Stop
    redis.close()
    await redis.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())

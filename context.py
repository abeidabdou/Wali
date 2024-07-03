from redis.asyncio import Redis
import os
from dotenv import load_dotenv

load_dotenv()

EXPIRATION_TIME = 300 # Context expiration time in seconds, modify it to your liking 

async def store_user_data(user_id, guild_id, data_type, data):
    key = f"user:{user_id}:{guild_id}"

    await redis.rpush(key, f"{data_type}: {data}")
    await redis.expire(key, EXPIRATION_TIME)


async def get_previous_interactions(user_id, guild_id):
    key = f"user:{user_id}:{guild_id}"
    interactions = await redis.lrange(key, 0, -1)
    formatted_interactions = "\n".join(interactions)
    return formatted_interactions


async def initialize_redis():
    global redis
    redis = Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        password=os.getenv('REDIS_PASSWORD'),
        encoding='utf-8',
        decode_responses=True
    )
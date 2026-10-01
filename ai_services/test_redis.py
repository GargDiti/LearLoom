
import asyncio

from services.redis_cache import (
    get_cached_value,
    set_cached_value,
    delete_cached_value,
    check_redis_connection,
)


async def main():
    key = "learnloom:test:redis"

    connected = await check_redis_connection()
    print("Redis connected:", connected)

    if not connected:
        print("Check your credentials and network connection.")
        return

    sample = {
        "topic": "Node.js Event Loop",
        "explanation": "The event loop coordinates asynchronous callbacks.",
    }

    saved = await set_cached_value(
        key,
        sample,
        ttl_seconds=60,
    )
    print("Saved:", saved)

    retrieved = await get_cached_value(key)
    print("Retrieved:", retrieved)

    assert retrieved == sample, "Retrieved data does not match!"

    await delete_cached_value(key)
    print("Deleted test key.")

    print("Redis test passed!")


if __name__ == "__main__":
    asyncio.run(main())
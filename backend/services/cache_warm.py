"""
This creates cache as soon as the app launches with 1 async function
its low-level too, so as everywhere else, i'll handle it
on the most abstracted layer. Not here.
"""

from redis.asyncio import Redis


async def warm_cache(collection: list, redis: Redis):
    """
    the collection is all the phrases and whatnot...
    """
    pass
    # await asyncio.gather(*tasks)
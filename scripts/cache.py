import logging
import redis
import asyncio
import requests, json, os, time, logging, sys

class Cache:
    def __init__(self, *args, **kwargs):
        self.redis = kwargs.get('redis', redis.Redis(host='redis', port=6379))
        self.logger = kwargs.get('logger', logging.getLogger('cache'))
    
    def get(self, url):
        return self.redis.get(url)

    def clear(self):
        self.redis.flushdb()

    async def getJsonFromUrl(self,url, session, retries = 5):
        for i in range(retries):
            try:
                async with session.get(url) as response:
                    return await response.text()
            except Exception as e:
                self.logger.error(e)
                self.logger.error("retry {i} {url}" .format(i=i, url=url))
                await asyncio.sleep(1)
        return None


    async def getJson(self, url, session):
        self.logger.debug("get cache for {}".format(url))
        if self.redis.exists(url):
            self.logger.debug("cache hit")
            cached = self.redis.get(url)
            return json.loads(cached)
        else:
            self.logger.debug("cache miss")
            data = await self.getJsonFromUrl(url, session)
            if data is not None:
                self.logger.debug("cache set")
                self.redis.set(url, data)
                return json.loads(data)
            else:
                return None
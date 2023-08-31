import dns.resolver
from motor.motor_asyncio import AsyncIOMotorClient

from app import Config

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ["8.8.8.8"]


class DataBase:
    def __init__(self):
        self._client = AsyncIOMotorClient(Config.DB_URL)
        self.db = self._client["d_v"]
        self.USERS = self.db.USERS
        self.BANNED = self.db.BANNED
        self.BANNER_REQUESTS = self.db.BANNER_REQUESTS

    def __getattr__(self, attr):
        try:
            return self.__dict__[attr]
        except KeyError:
            self.__dict__[attr] = self.db[attr]
            return self.__dict__[attr]


DB = DataBase()

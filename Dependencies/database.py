from pymongo import MongoClient
import os
from dotenv import load_dotenv
import redis

load_dotenv()

class DB:
    
    def __init__(self):
        self.client = MongoClient(os.getenv('mongo'))
        self.cluster = self.client['price_platform']
        self.product = self.cluster['product']
        self.users = self.cluster['User']
        self.tracks = self.cluster['tracks']
        self.email = self.cluster['email']
        self.passwordreset = self.cluster['PasswordReset']


class Redis:

    def __init__(self):
        self.cache = redis.Redis(
                    host= os.getenv('redis_host'),
                    port=10162,
                    decode_responses=True,
                    username="default",
                    password= os.getenv('redis_password'),
                    )
        self.verification = 'verification'
    #     self.createHash()

    # def createHash(self):
    #     hashSet = self.cache.hset(f"{self.verification}:name", mapping={
    #         'name' : 'gayashan',
    #         'school' : 'NRC',
    #         'university' : 'ousl',
    #     })
    #     if hashSet == True:
    #         print('transaction is success')
    #         return 
    #     elif hashSet == False:
    #         print('transaction is not success')
    #         pass
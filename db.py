import os, redis
from urllib.parse import urlparse

url = urlparse(os.environ.get('REDISCLOUD_URL'))
accounts = redis.Redis(host=url.hostname, port=url.port, password=url.password)

def addAcc(nick):
    accounts.set(nick, 15)

def removeAcc(nick):
    accounts.delete(nick)

def transfer(giver, receiver, amount):
    pipe = accounts.pipeline()
    pipe.incrby(receiver, amount)
    pipe.decrby(giver, amount)
    pipe.execute()

def checkBal(nick):
    return accounts.get(nick)

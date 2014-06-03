import os, redis
from urllib.parse import urlparse

url = urlparse(os.environ.get('REDISCLOUD_URL'))
accounts = redis.Redis(host=url.hostname, port=url.port)

def addAcc(nick):
    accounts.set(nick, 15)

def removeAcc(nick):
    accounts.delete(nick)

def transfer(giver, receiver, amount):
    if int(accounts.get(giver)) - amount >= 0 and amount > 0:
        pipe = accounts.pipeline()
        pipe.incrby(receiver, amount)
        pipe.incrby(giver, -amount)
        pipe.execute()
        return True
    else:
        return False

def checkBal(nick):
    try:
        return int(accounts.get(nick))
    except:
        return False

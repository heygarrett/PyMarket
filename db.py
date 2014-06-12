import redis

accounts = redis.Redis('127.0.0.1', '6379')

def removeAcc(nick):
    accounts.delete(nick)

def transfer(server, giver, receiver, amount):
    accounts.hsetnx(server, giver, 15)
    accounts.hsetnx(server, receiver, 15)
    if checkBal(server, giver) - amount >= 0:
        pipe = accounts.pipeline()
        pipe.hincrby(server, receiver, amount)
        pipe.hincrby(server, giver, -amount)
        pipe.execute()
        return True
    else:
        return False

def checkBal(server, nick):
    try:
        return int(accounts.hget(server, nick))
    except:
        return 15

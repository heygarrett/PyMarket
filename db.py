import redis

accounts = redis.Redis('127.0.0.1', '6379')

def addAcc(nick):
    if not checkBal(nick):
        accounts.set(nick, 15)

def removeAcc(nick):
    accounts.delete(nick)

def transfer(giver, receiver, amount):
    if int(accounts.get(giver)) - amount >= 0:
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

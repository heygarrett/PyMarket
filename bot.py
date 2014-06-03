import re, irc, db

class Pymarket:

    def __init__(self, connection):
        self.irc = connection
        self.users = []
        self.handlers = {
                'PRIVMSG': self.message,
                'JOIN': self.join,
                'QUIT': self.leave,
                'PART': self.leave,
                'KICK': self.leave,
                'KILL': self.leave,
                '353': self.names
        }

    def parse_message(self, line):
        values = {}
        if line[0] == ':' and '!' in line:
            prefix, line = line[1:].split(' ', 1)
            values['nick'] = prefix.split('!')[0]
            values['command'], values['target'], line = line.split(' ', 2)
        if ' :' in line:
            values['text'] = line.split(' :')
        if len(values) == 4:
            choice = self.handlers.get(values['command'])
            if choice:
                choice(values)

    def message(self, values):
        print(values['nick'] + ': ' + values['text'])

    def join(self, values):
        self.users.append(values['nick'])
        print('%s joined %s' % (values['nick'], values['target']))

    def leave(self, values):
        self.users.remove(values['nick'])
        print('%s left' % values['nick'])
        
    def names(self, values):
        self.users += values['nick']
        print(self.users)
        for i in self.users:
            if not db.checkBal(i):
                db.addAcc(i)

def main():
    connection = irc.Irc('irc.freenode.net', 6667, 'PyMarket', '#gyaretto')
    bot = Pymarket(connection)
    connection.connect()
    while True:
        line = connection.receive()
        if line:
            print(line)
            bot.parse_message(line)

if __name__ == "__main__":
    main()

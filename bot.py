import re, irc, db

class Pymarket:

    def __init__(self, connection):
        self.irc = connection
        self.users = []
        self.handlers = {
                'PRIVMSG': self.message,
                'NOTICE': self.notice,
                'JOIN': self.join,
                'QUIT': self.leave,
                'PART': self.leave,
                'KICK': self.leave,
                'KILL': self.leave,
                '353': self.names
        }

    def parse_message(self, line):
        values = {}
        if line[0] == ':':
            prefix, line = line[1:].split(' ', 1)
            values['nick'] = prefix.split('!')[0]
            values['command'], line = line.split(' ', 1)
        if ' :' in line:
            values['target'], values['text'] = line.split(' :', 1)
        if len(values) >= 3:
            choice = self.handlers.get(values['command'])
            if choice:
                choice(values)
        if line.split()[0] == 'PING':
            self.irc.send('PONG', line.split()[1])

    def message(self, values):
        if values['target'] == 'PyMarket':
            self.notice(values)
            return
        command = values['text'].split()[0]
        if '+=' in command:
            nick, credits = command.split('+=', 1)
            try:
                credits = int(credits)
                if nick in self.users and credits > 0:
                    success = db.transfer(values['nick'], nick, credits)
                    if success:
                        self.irc.send('PRIVMSG', values['target'], ':Credits transferred from', \
                                values['nick'], 'to', nick + ':', str(credits))
                    else:
                        self.irc.send('PRIVMSG', values['target'], ':' + values['nick'], ': Not enough credits')
            except ValueError:
               print('Credits not a number.')
        print(values['nick'] + ': ' + values['text'])

    def notice(self, values):
        if 'credits' in values['text']:
            self.irc.send('NOTICE', values['nick'], ':', str(db.checkBal(values['nick'])))

    def join(self, values):
        self.users.append(values['nick'])
        print('%s joined %s' % (values['nick'], values['target']))

    def leave(self, values):
        self.users.remove(values['nick'])
        print('%s left' % values['nick'])
        
    def names(self, values):
        self.users = values['text'].split()
        print(self.users)
        for user in self.users:
            if not db.checkBal(user):
                db.addAcc(user)

def main():
    connection = irc.Irc('irc.freenode.net', 6667, 'PyMarket', '#gyaretto')
    bot = Pymarket(connection)
    connection.connect()
    while True:
        line = connection.receive()
        if line:
            for text in line:
                print(text)
                bot.parse_message(text)

if __name__ == "__main__":
    main()

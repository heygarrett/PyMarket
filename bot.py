import re, irc, db, sys

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
            line = line[1:].split(' ', 1)
            if '!' in line[0]:
                values['nick'] = line[0].split('!')[0]
            line = line[1]
        if ' :' in line:
            line, values['text'] = line.split(' :', 1)
        args = line.split()
        values['command'] = args.pop(0)
        if len(args) >= 1:
            values['target'] = args.pop(-1)
        else:
            values['target'] = values['text']
            del values['text']
        print('values: ', values)
        if len(values) >= 3:
            choice = self.handlers.get(values['command'])
            if choice:
                choice(values)
        if line.split()[0] == 'PING':
            self.irc.send('PONG', line.split()[1])

    def message(self, values):
        print(values['nick'] + ': ' + values['text'])
        sys.stdout.flush()

        if values['target'] == self.irc.name:
            self.notice(values)
            return
        try:
            command = values['text'].split()[0]
        except:
            return
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
                pass
        if self.irc.name in command and 'help' in values['text']:
            self.irc.send('PRIVMSG', values['target'], ':' + '\"<nick>+=X\" will transfer X credits to <nick>.')
            self.irc.send('PRIVMSG', values['target'], ':' + \
                    'PM or NOTICE PyMarket with the word \"credits\" to see your credits.')

    def notice(self, values):
        if 'credits' in values['text']:
            self.irc.send('NOTICE', values['nick'], ':', str(db.checkBal(values['nick'])))

    def join(self, values):
        self.users.append(values['nick'])
        print('%s joined %s' % (values['nick'], values['target']))
        sys.stdout.flush()

    def leave(self, values):
        self.users.remove(values['nick'])
        print('%s left' % values['nick'])
        sys.stdout.flush()
        
    def names(self, values):
        for nick in values['text'].split():
            self.users.append(re.match('^[~&@%+]?(.*)$', nick).group(1))
        for user in self.users:
            sys.stdout.flush()
            if not db.checkBal(user):
                db.addAcc(user)

def main():
    connection = irc.Irc('mccs.stu.marist.edu', 6667, 'PyMarket', '#chat')
    bot = Pymarket(connection)
    connection.connect()
    while True:
        line = connection.receive()
        for text in line:
            print(text)
            sys.stdout.flush()
            bot.parse_message(text)

if __name__ == "__main__":
    main()

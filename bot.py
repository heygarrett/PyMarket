import re, irc, db, threading

class Pymarket:

    def __init__(self, connection):
        self.irc = connection
        self.users = set()
        self.handlers = {
            'PRIVMSG': self.message,
            'NOTICE': self.notice,
            'JOIN': self.join,
            'QUIT': self.leave,
            'PART': self.leave,
            'KICK': self.kick,
            'KILL': self.kick,
            'NICK': self.nick,
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
            if line == 'PING':
                self.irc.send('PONG', ':' + values['text'])
        args = line.split()
        values['command'] = args.pop(0)
        if len(args) == 2:
            values['target'], values['extra'] = args
        elif len(args) == 1:
            values['target'] = args[0]
        choice = self.handlers.get(values['command'])
        if choice:
            choice(values)

    def message(self, values):
        if values['target'] == self.irc.name:
            self.notice(values)
            return
        try:
            command = values['text'].split()[0]
        except:
            return
        if '+=' in command:
            rcv, credits = command.split('+=', 1)
            try:
                credits = int(credits)
                if rcv in self.users and credits > 0 and values['nick'] != rcv:
                    if db.transfer(values['nick'], rcv, credits):
                        self.irc.send(
                            'PRIVMSG', values['target'], 
                            ':Credits transferred from', values['nick'], 
                            'to', rcv + ':', str(credits))
                    else:
                        self.irc.send(
                            'PRIVMSG', values['target'], 
                            ':' + values['nick'] + ': Not enough credits.')
            except ValueError:
                pass
        test = re.match('(\\w+)[:,]?', command)
        if test:
            if self.irc.name == test.group(1) and 'help' in values['text']:
                self.irc.send(
                    'PRIVMSG', values['target'], 
                    ':' + '\"<nick>+=X\" will transfer X credits to <nick>.')
                self.irc.send(
                    'PRIVMSG', values['target'], 
                    ':' + 'PM or NOTICE PyMarket with '
                    '<nick> to see <nick>\'s credits.')

    def notice(self, values):
        if db.checkBal(values['text']):
            self.irc.send(
                    'NOTICE', values['nick'], ':' + values['text'], 
                    'has', str(db.checkBal(values['text'])), 'credits.')

    def join(self, values):
        self.users.add(values['nick'])
        db.addAcc(values['nick'])

    def leave(self, values):
        if values['nick'] in self.users:
            self.users.remove(values['nick'])

    def kick(self, values):
        if values['extra'] in self.users:
            self.users.remove(values['extra'])

    def nick(self, values):
        self.users.add(values['text'])
        db.addAcc(values['text'])
        if values['nick'] in self.users:
            self.users.remove(values['nick'])
        
    def names(self, values):
        for nick in values['text'].split():
            self.users.add(re.match('^[~&@%+]?(.+)$', nick).group(1))
        for user in self.users:
            db.addAcc(user)

def main():

    def startBot(bot):
        bot.irc.connect()
        while True:
            lines = bot.irc.receive()
            for text in lines:
                text = text.decode('utf-8', 'replace')
                print(text)
                bot.parse_message(text)

    freenodeConnect = irc.Irc(
        'irc.freenode.net', 6667, 
        'PyMarket', '#learnprogramming,#lpmc')
    mccsConnect = irc.Irc(
        'mccs.stu.marist.edu', 6667, 
        'PyMarket', '#chat')
    freenode = Pymarket(freenodeConnect)
    mccs = Pymarket(mccsConnect)
    threading.Thread(target=startBot, args=(freenode,)).start()
    threading.Thread(target=startBot, args=(mccs,)).start()

if __name__ == '__main__':
    main()

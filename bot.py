import re, irc, db, threading, config

class Pymarket:

    def __init__(self, serverName, connection):
        self.server = serverName
        self.irc = connection
        # Keeping a set of users makes for easy checks for who's present
        self.users = set()
        # Using a dictionary makes it easy to call the correct method by
        # matching the command sent by the server with a key.
        self.handlers = {
            'PRIVMSG': self.message,
            'NOTICE': self.notice,
            'JOIN': self.join,
            'QUIT': self.leave,
            'PART': self.leave,
            'KICK': self.kick,
            'KILL': self.kick,
            'NICK': self.nick,
            'PING': self.ping,
            '353': self.names
        }

    # Parses each line from the server.
    # Receives line as a parameter.
    def parseMessage(self, line):
        # Splits each line into three main components:
        # prefix, command, and params.
        values = {}
        if line[0] == ':':
            values['prefix'], line = line[1:].split(' ', 1)
        if ' :' in line:
            line, values['text'] = line.split(' :', 1)
        line = line.split(' ', 1)
        if len(line) > 1:
            values['command'] = line[0]
            values['params'] = line[1]
        elif len(line) == 1:
            values['command'] = line[0]

        # Further splits those components into usable pieces stored in the 
        # values dictionary.
        if 'prefix' in values and '!' in values['prefix']:
            values['nick'] = values['prefix'].split('!', 1)[0]
        if 'params' in values and ' :' in values['params']:
            values['params'] = values['params'].split()
            values['target'] = values['params'].pop(0)
            if len(values['params']) > 0:
                values['extra'] = values['params'].pop(0)

        # Matches the server command with the correct handler, making it easy 
        # to call the correct method for that command.
        choice = self.handlers.get(values['command'])
        if choice:
            choice(values)

    # Handles messages from PRIVMSG commands.
    # NEEDS A REWRITE
    def message(self, values):
        # Passes values to the notice method if the message target is the bot.
        # Then exits method.
        if values['target'] == self.irc.name:
            self.notice(values)
            return
        # Exits method if values['text'] contains nothing but spaces.
        try:
            command = values['text'].split()[0]
        except:
            return

        # Creates transaction when the transaction syntax is recognized.
        if '+=' in command:
            rcv, credits = command.split('+=', 1)
            # An exception is raised if credits does not exist.
            # e.g. PyMarket+=
            try:
                credits = int(credits)
                if rcv in self.users and credits > 0 and values['nick'] != rcv:
                    if db.transfer(self.server, values['nick'], rcv, credits):
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
        # Checks to see if the help command is issued and responds accordingly.
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

    # Responds to requests for credit checks.
    def notice(self, values):
        numCredits = None
        if db.checkBal(self.server, values['text']):
            numCredits = db.checkBal(self.server, values['text'])
        elif values['text'] in self.users:
            numCredits = 15
        if numCredits != None:
            self.irc.send(
                'NOTICE', values['nick'], ':' + values['text'], 
                'has', str(numCredits), 'credits.')

    # Adds each user that joins to the set of present users.
    def join(self, values):
        self.users.add(values['nick'])

    # Removes each user that leaves from the set of present users.
    def leave(self, values):
        if values['nick'] in self.users:
            self.users.remove(values['nick'])

    # Removes each user that is kicked from the set of present users.
    def kick(self, values):
        if values['extra'] in self.users:
            self.users.remove(values['extra'])

    # Removes old nick from and adds new nick to set of present users.
    def nick(self, values):
        self.users.add(values['text'])
        if values['nick'] in self.users:
            self.users.remove(values['nick'])

    # Responds to PINGs from the server.
    def ping(self, values):
        self.irc.send('PONG', ':' + values['params'])
        
    # Adds all nicks to set of present users when the bot joins.
    def names(self, values):
        for nick in values['text'].split():
            self.users.add(re.match('^[~&@%+]?(.+)$', nick).group(1))

def main():

    # Starts the bot and puts it in a receiving loop.
    def startBot(bot):
        bot.irc.connect()
        while True:
            lines = bot.irc.receive()
            for text in lines:
                text = text.decode('utf-8', 'replace')
                print(text)
                bot.parseMessage(text)

    # Creates a thread for each instance in config.servers.
    for server in config.servers:
        connection = irc.Irc(
            server['url'], server['port'],
            server['nick'], server['channels'])
        bot = Pymarket(server['name'], connection)
        threading.Thread(target=startBot, args=(bot,)).start()
        
if __name__ == '__main__':
    main()

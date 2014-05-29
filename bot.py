import socket, re

class Pymarket(object):

    def __init__(self, host, port, name, channel):
        self.host = host
        self.port = port
        self.name = name
        self.channel = channel
        self.options = {
                'PRIVMSG': self.message,
                'JOIN': self.join,
                'QUIT': self.leave,
                'PART': self.leave,
                'KICK': self.leave,
                'KILL': self.leave,
                '353': self.names
        }

    def send(self, data):
        self.irc.send(data.encode())

    def connect(self):
        self.irc = socket.socket()
        self.irc.connect((self.host, self.port))
        self.send('NICK %s\r\n' % self.name)
        self.send('USER %s %d %s :%s\r\n' % (self.name, 8, '*', self.name))
        self.send('JOIN %s\r\n' % self.channel)

    def parse_message(self, message):
        self.sections = message.split(':')
        if self.sections[0] == '':
            keys = ['sender', 'type', 'target']
            self.args = dict((key, value) for key, value in zip(keys, self.sections[1].split()))
            if '!' in self.args['sender']:
                self.args['sender'] = self.args['sender'][0:self.args['sender'].index('!')]
            if self.args['type'] == 'PRIVMSG':
                self.args['message'] = ':'.join(self.sections[2:])

            choice = self.options.get(self.args['type'])
            if choice:
               choice()
        elif self.sections[0] == 'PING':
            print('Ping!')
            self.send('PONG :%s\r\n' % self.sections[1])
            print('Pong!')

    def message(self):
        print('%s: %s' % (self.args['sender'], self.args['message']))

    def join(self):
        print('%s joined %s' % (self.args['sender'], self.args['target']))

    def leave(self):
        print('%s left' % self.args['sender'])
        
    def names(self):
        c = re.compile('[^\\w -]')
        nicks = c.sub('', self.sections[2]).split()
        print(nicks)

def main():
    client = Pymarket('irc.freenode.net', 6667, 'PyMarket', '#gyaretto')
    client.connect()
    while True:
        server_message = client.irc.recv(4096).decode()
        client.parse_message(server_message)

if __name__ == '__main__':
    main()

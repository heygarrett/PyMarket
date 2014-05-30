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
        line = data + '\r\n'
        self.irc.send(line.encode())

    def connect(self):
        self.irc = socket.socket()
        self.irc.connect((self.host, self.port))
        self.send('NICK %s' % self.name)
        self.send('USER %s %d %s :%s' % (self.name, 8, '*', self.name))
        self.send('JOIN %s' % self.channel)

    def parse_message(self, line):
        sections = line.split(':')
        if sections[0] == '':
            keys = ['sender', 'type', 'target']
            sm = dict((key, value) for key, value in zip(keys, sections[1].split()))
            if '!' in sm['sender']:
                sm['sender'] = sm['sender'][0:sm['sender'].index('!')]
            if sm['type'] == 'PRIVMSG':
                sm['text'] = ':'.join(sections[2:])
            if sm['type'] == '353':
                c = re.compile('[^\\w -]')
                sm['nicks'] = c.sub('', sections[2]).split()

            choice = self.options.get(sm['type'])
            if choice:
               choice(sm)
               
        elif sections[0] == 'PING':
            print('Ping!')
            self.send('PONG :%s\r\n' % sections[1])
            print('Pong!')

    def message(self, args):
        print('%s: %s' % (args['sender'], args['text']))

    def join(self, args):
        print('%s joined %s' % (args['sender'], args['target']))

    def leave(self, args):
        print('%s left' % args['sender'])
        
    def names(self, args):
        nicks = args['nicks']

def main():
    client = Pymarket('irc.freenode.net', 6667, 'PyMarket', '#gyaretto')
    client.connect()
    while True:
        line = client.irc.recv(4096).decode()
        client.parse_message(line)

if __name__ == '__main__':
    main()

import socket, re, db

class Pymarket(object):

    def __init__(self, host, port, name, channel):
        self.host = host
        self.port = port
        self.name = name
        self.channel = channel
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

    def send(self, *data):
        line = ' '.join(data) + '\r\n'
        self.irc.send(line.encode())

    def connect(self):
        self.irc = socket.socket()
        self.irc.connect((self.host, self.port))
        self.send('NICK', self.name)
        self.send('USER', self.name, '8', '*', self.name)
        self.send('JOIN', self.channel)

    def parse_message(self, line):
        sections = line.split(':')
        if sections[0] == '':
            keys = ['sender', 'type', 'target']
            serv_message = dict((key, value) for key, value in zip(keys, sections[1].split()))
            if '!' in serv_message['sender']:
                serv_message['sender'] = serv_message['sender'][0:serv_message['sender'].index('!')]
            if serv_message['type'] == 'PRIVMSG':
                serv_message['text'] = ':'.join(sections[2:])
            if serv_message['type'] == '353':
                c = re.compile('[^\\w -]')
                serv_message['nicks'] = c.sub('', sections[2]).split()

            choice = self.handlers.get(serv_message['type'])
            if choice:
               choice(serv_message)
               
        elif sections[0] == 'PING':
            self.send('PONG :%s\r\n' % sections[1])

    def message(self, sm):
        nick = sm['sender']
        text = sm['text'].split()

        for user in self.users:
            if user in text[0] and text[0].index(user) == 0:
                receiver = user
                print('receiver:', receiver)
                suffix = text[0].replace(user, '')
                credits = rg.match('^\\+=(\\d+)?$', suffix).group(1)
                print('credits:', credits)
                break

        if receiver and credits:
            db.transfer(nick, receiver, credits)
            self.send('Credits transferred from', nick, 'to', receiver, ':', credits)

    def join(self, sm):
        self.users.append(sm['sender'])
        print('%s joined %s' % (sm['sender'], sm['target']))

    def leave(self, sm):
        self.users.remove(sm['sender'])
        print('%s left' % sm['sender'])
        
    def names(self, sm):
        self.users += sm['nicks']
        print(self.users)
        for i in self.users:
            if not db.checkBal(i):
                db.addAcc(i)

def main():
    client = Pymarket('irc.freenode.net', 6667, 'PyMarket', '#gyaretto')
    client.connect()
    buf = ''
    while True:
        buf += client.irc.recv(4096).decode()
        if '\r\n' in buf:
            line = buf[:buf.index('\r\n')]
            buf = buf[buf.index('\r\n') + 1:]
            client.parse_message(line)
            print(line)

if __name__ == '__main__':
    main()

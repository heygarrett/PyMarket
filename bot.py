import socket, re

class Pymarket(object):

    def __init__(self, host, port, name, channel):
        self.host = host
        self.port = port
        self.name = name
        self.channel = channel

    def send(self, data):
        self.irc.send(data.encode())

    def connect(self):
        self.irc = socket.socket()
        self.irc.connect((self.host, self.port))
        self.send("NICK %s\r\n" % self.name)
        self.send("USER %s %d %s :%s\r\n" % (self.name, 8, "*", self.name))
        self.send("JOIN %s\r\n" % self.channel)

    def parse_message(self, message):
        if message.split()[0] == "PING":
            self.send("PONG %s\r\n" % message.split()[1])
        else:
            keys = ['sender', 'command', 'target', 'message']
            self.args = dict((key, value.lstrip(':')) for key, value in zip(keys, message.split()))
            self.args['sender'] = self.args['sender'][0:self.args['sender'].index('!')]

            if self.args['command'] == "PRIVMSG":
                self.message()
            elif self.args['command'] == "JOIN":
                self.join()
            elif self.args['command'] == "QUIT":
                self.leave()
            elif self.args['command'] == "PART":
                self.leave()
            elif self.args['command'] == "KICK":
                self.leave()
            elif self.args['command'] == "KILL":
                self.leave()

    def message(self):
        print("%s: %s" % (self.args['sender'], self.args['message']))

    def join(self):
        print("%s joined %s" % (self.args['sender'], self.args['target']))

    def leave(self):
        print("%s left %s" % (self.args['sender'], self.args['target']))

def main():
    client = Pymarket("irc.freenode.net", 6667, "pymarket", "#learnprogramming")
    client.connect()
    while True:
        server_message = client.irc.recv(4096).decode()
        client.parse_message(server_message)

if __name__ == "__main__":
    main()

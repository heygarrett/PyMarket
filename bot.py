import socket

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
        self.words = message.decode().split()
        if self.words[0] == "PING":
            self.irc.send("PONG %s\r\n" % words[1])

def main():
    client = Pymarket("irc.freenode.net", 6667, "pymarket", "#learnprogramming")
    client.connect()
    while True:
        server_message = client.irc.recv(4096)
        client.parse_message(server_message)

if __name__ == "__main__":
    main()

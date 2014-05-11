# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import obelisk
import json
import sys
import time
import urllib2

def read_binfo():
    url = "https://blockchain.info/latestblock"
    f = urllib2.urlopen(url)
    return json.loads(f.read())

class LogBot(irc.IRCClient):

    nickname = "darkbot11"
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        pass

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        print user, channel, msg
        
        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "It isn't nice to whisper!  Play nice with the group."
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        if msg.startswith("!"):
            self.factory.client.fetch_last_height(self.height_fetched)

    def height_fetched(self, ec, height):
        if ec:
            self.msg(self.factory.channel, "Error: %s" % ec)
            return
        try:
            binfo_height = read_binfo()["height"]
        except:
            binfo_height = None
        self.msg(self.factory.channel,
            "Obelisk: %s   blockchain.info: %s" % (height, binfo_height))

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]

    def irc_NOTICE(self, prefix, params):
        print prefix, params
    #def irc_PRIVMSG(self, prefix, params):
    #    print prefix, params
    #def irc_ERR_NICKNAMEINUSE(self, prefix, params):
    #    print prefix, params
    #def irc_ERR_PASSWDMISMATCH(self, prefix, params):
    #    print prefix, params


    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '_'



class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, channel):
        self.channel = channel
        self.client = obelisk.ObeliskOfLightClient("tcp://localhost:9091")

    def buildProtocol(self, addr):
        p = LogBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)
    
    # create factory protocol and application
    f = LogBotFactory("#darkwallet")

    # connect factory to this host and port
    reactor.connectTCP("irc.freenode.net", 6667, f)

    # run bot
    reactor.run()

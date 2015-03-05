from parser import Parser
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, \
                                            WebSocketServerProtocol


# manage connection in a dictionary
# store connection along with username
connection_pool = {}


class MHomeServerProtocol(WebSocketServerProtocol):
    """
    Sensors server to manage websocket connections, basically create wesocket
    connection and listen to it
    Incoming messges parse by QueryParser and delegate task to approprite
    manager according to Query
    """
    def onConnect(self, response):
        """
        call when connect to websocker
        """
        print '-----------------------'
        print '--------CONNECT--------'
        print '-----------------------\n'

    def onOpen(self):
        """
        call when open websocket
        initialize all globle parameters here
        """
        print '-----------------------'
        print '---------OPEN----------'
        print '-----------------------\n'

    def onClose(self, wasClean, code, reason):
        """
        call when closing websocket
        reset all globale parametes and connections here

        remove connection from connection pool
        """
        print '-----------------------'
        print '--------CLOSE----------'
        print '-----------------------\n'
        # remove connection from pool
        user = self.get_user(self)
        if user is not None:
            del connection_pool[user]

    def onMessage(self, msg, binary):
        """
        call when message receives to listning websocket
        message will be parse by QueryParser and delegate task to appropriate
        manages according to QueryParser resuslt(result will be Query object),
        following tasks can be perform according to QueryParser result
            1. Login - Login user to system
            2. Share - Share data between users, manage Share request
            3. Get - Manage get query requests
            4. Create - Create users, manage create requests
        """
        # parse message and get query result
        # currently we support fro only valid queries
        # we assume incoming 'msg' is valid message
        print '-----------------------'
        print msg
        print '-----------------------\n'
        parser = Parser()
        query = parser.parse(message=msg)

        if query.command == 'LOGIN':
            # delegate to handle_login
            self.handle_login(binary=binary, query=query)

        elif query.command == 'PUT':
            # delegate task to handle_put
            self.handle_put(binary=binary, query=query)

        elif query.command == 'DATA':
            # delegate task to handle_put
            connection_pool[query.user].sendMessage('DONE', binary)

    def handle_login(self, binary, query):
        """
        handle login functaionlity of users
        currently login users and connecgtions stored in 'connection_pool'
        need to check user alredy have a connection in 'connection_pool' if
        have a connection need to ignore request
        otherwise need to create new connection for this user(creating
        means adding websocket connection to connection_pool)

        finally create status query and send it to corresponding user, status
        query contains Login success/fail status

        currently we dont authnticate users, istade just create connections for
        all requests. need to add mechanism to authenticate users here

        Args:
            query: generated query

        Returns:
            login success or not
        """
        user = query.parameters['username']
        if user not in connection_pool:
            # add user if user dosent have connection yet
            # we store web socket connections in connection_pool
            connection_pool[user] = self

            self.sendMessage('LOGIN_SUCCESS', binary)
        else:
            # alredy have a connection
            # login fail
            self.sendMessage('LOGIN_FAIL', binary)

    def handle_put(self, binary, query):
        """
        handle PUT query here(switching queries)
        """
        # verify requesting user(currently connected/self user)
        # if authenticated current connection/self should be in connecion_pool
        if self in connection_pool.values():
            # verify PUT user have a connection (logged in)
            # user need to be logged in to continue
            if query.user in connection_pool:
                # find current user from connection pool
                request_user = self.get_user(self)

                # replace user parameter in query
                # send query to matching user
                swaped_query = query.command + ' #switch ' +  \
                        query.parameters['switch'] + ' @' + request_user
                connection_pool[query.user].sendMessage(swaped_query, binary)

    def get_user(self, connection):
        """
        get matching user for given connection
        connection_pool stores connections along with users (user as key and
        connection as values), we have extract the key(user) which is
        corresponds to connection

        Args:
            connection: wen socket connecction

        Returnds:
            matching user if avaiable otherwise None
        """
        # extract from dictionary key, value pairs
        for key, value in connection_pool.items():
            if value == connection:
                # key is the user
                return key

        return None


if __name__ == '__main__':
    # start web socket server
    # we listen to websocket on 10.2.4.14:9000
    factory = WebSocketServerFactory("ws://10.2.2.132:9000")
    factory.protocol = MHomeServerProtocol

    reactor.listenTCP(9000, factory)
    reactor.run()

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

        elif query.command == 'GET' or query.command == 'DATA':
            # delegate task to handle_get
            self.handle_get(query)

        elif query.command == 'SHARE':
            # delegate to handle_share
            self.handle_share(binary=binary, query=query)

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
        # use default status to 'success'
        status = 'success'

        # TODO implement authentication mechnism
        user = query.parameters['username']
        if user not in connection_pool:
            # add user if user dosent have connection yet
            # we store web socket connections in connection_pool
            connection_pool[user] = self
        else:
            # alredy have a connection
            # login fail
            status = 'fail'

        # get loing status message and send too user
        #status = self.get_status_query(query, status)
        status = "PUT #switch kitchen @eranga"
        self.sendMessage(status, binary)

    def handle_share(self, binary, query):
        """
        handle sharing functionality between users
        when Share query comes need to veryfy sharing users, then need to swap
        query parametes and send to matching user

        for a instance, if query comes 'SHARE #tp @user1', first need to veryfy
        user1 is logged in, if logged in need to replace 'user1' with
        requesting users username (for a instance 'user2'). for final query
        would be 'SHARE #tp @user2' and it sends to user1

        finally create status query and send it to corresponding user, status
        query contains SHARE success/fail status

        to complete sharing sharing user and requesting user need to logged in
        to the system

        Args:
            query: generated query

        Returns:
            share success or not
        """
        # use default status to 'success'
        status = 'success'

        # verify requesting user(currently connected/self user)
        # if authenticated current connection/self should be in connecion_pool
        if self in connection_pool.values():
            # verify shareing user have a connection (logged in)
            # user need to be logged in to continue
            if query.user in connection_pool:
                # find current user from connection pool
                request_user = self.get_user(self)

                # replace user parameter in query
                # send query to matching user
                swaped_query = self.swap_query(query, request_user)
                connection_pool[query.user].sendMessage(swaped_query,
                                                        False)
            else:
                # user dont have connection
                # teminate share request
                status = 'fail'
        else:
            # unauthenticated user
            status = 'fail'

        # get share status message and send to user
        status = self.get_status_query(query, status)
        self.sendMessage(status, binary)

    def handle_get(self, query):
        """
        handle sharing functionality between users
        when Share query comes need to veryfy sharing users, then need to swap
        query parametes and send to matching user

        for a instance, if query comes 'SHARE #tp @user1', first need to veryfy
        user1 is logged in, if logged in need to replace 'user1' with
        requesting users username (for a instance 'user2'). for final query
        would be 'SHARE #tp @user2' and it sends to user1

        to complete sharing sharing user and requesting user need to logged in
        to the system

        Args:
            query: generated query

        Returns:
            share success or not
        """
        # verify requesting user(currently connected/self user)
        # if authenticated current connection/self should be in connecion_pool
        if self in connection_pool.values():
            # verify shareing user have a connection (logged in)
            # user need to be logged in to continue
            if query.user in connection_pool:
                # find current user from connection pool
                request_user = self.get_user(self)

                # differnet scenario for DATA queries
                # swaping happend in difernt way
                if query.command == 'DATA':
                    swapped_data_query = self.swap_data_query(query,
                                                              request_user)
                    connection_pool[query.user].sendMessage(swapped_data_query,
                                                            False)

                    return True

                # replace user parameter in query
                # send query to matching user
                swaped_query = self.swap_query(query, request_user)
                connection_pool[query.user].sendMessage(swaped_query,
                                                        False)
                return True

            else:
                # user dont have connection
                # teminate share request
                return False
        else:
            # unauthenticated user
            return False

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

    def swap_query(self, query, user):
        """
        replace user in query onbject and generate new query string

        for a instance, if query comes 'SHARE #tp @user1', first need to veryfy
        user1 is logged in, if logged in need to replace 'user1' with
        requesting users username (for a instance 'user2'). for final query
        would be 'SHARE #tp @user2' and it sends to user1

        Args:
            query: Query object
            user: new user

        returns:
            swapped query
        """
        return query.command + " " + query.parameters['param'] + " @" + user

    def swap_data_query(self, query, user):
        """
        replace user in query onbject and generate new query string, we have
        query attributes in DATA queries so need to add them as well wend
        swapping

        for a instance, if query comes 'DATA #gps colombo  @user1', first need
        to veryfy user1 is logged in, if logged in need to replace 'user1' with
        requesting users username (for a instance 'user2'). for final query
        would be 'DATA #gps colombo @user2' and it sends to user1

        Args:
            query: Query object
            user: new user

        returns:
            swapped query
        """
        # TODO add DATA query swaping logic
        return query.command + " " + "#gps " + query.parameters['gps'] + \
                                                                " @" + user

    def get_status_query(self, query, status):
        """
        generate status query for login and share
        this inculde LOGIN and SHARE success/fail status
        for a instance
            1. login success    LOGIN #status success
            2. login fail       LOGIN #status fail
            3. share succcess   SHARE @user1 #status success
            4. share fail       SHARE @user1 #status fail

        Args:
            query: Query object
            status: sucess/fail status

        Returns:
            status query
        """
        status_query = "STATUS" + " #" + query.command + " " + status
        return status_query


if __name__ == '__main__':
    # start web socket server
    # we listen to websocket on 10.2.4.14:9000
    factory = WebSocketServerFactory("ws://10.2.2.132:9000")
    factory.protocol = MHomeServerProtocol

    reactor.listenTCP(9000, factory)
    reactor.run()

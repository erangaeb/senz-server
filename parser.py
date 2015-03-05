from query import Query


class Parser():
    """
    Query parser of sensor application
    incoming messages from websockets parser by Query Parser and get Query
    parametes
    according to query parametes, appropriate manager will be invokes
    """
    def parse(self, message):
        """
        Parse incoming message according to defin query formats
        have following examle query formts
            1. Login : LOGIN #username user1 #password test
            2. Get : GET #gps @user1
            3. Share : SHARE #gps @user1
            4. Data : DATA #gps colombo @user1
        Args:
            message: message to be parse

        Returns:
            query: Query object with query parameters
        """
        # define query commands
        # we support only for 4 commands
        command_list = ['LOGIN', 'GET', 'SHARE', 'DATA']

        # define to hold parametes and data
        command = 'LOGIN'
        user = 'test'
        parameters = {}

        # need to tokanize message beofr parsing
        token_list = message.split()

        # iterate over token list ad generate query
        while token_list:
            token = token_list.pop(0)

            if token in command_list:
                # command found
                command = token
            elif token.startswith('@'):
                # user found
                user = token[1:]
            elif token.startswith('#'):
                # query parameter fround
                # need to store in dictionlary
                if command == 'LOGIN' or command == 'DATA':
                    # differnet scenarion for LOGIN and DATA queries
                    # these queries comes with following format
                    #   field value (ex: #tp 30)
                    parameters[token[1:]] = token_list.pop(0)
                else:
                    # add parameter with 'param' key
                    parameters['param'] = token

        # TODO add error handling for invalid queries

        return Query(command=command, user=user, parameters=parameters)

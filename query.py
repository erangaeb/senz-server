class Query():
    """
    hold Query attributes
    just applain python object which holds followind data
        1. command: Query command ('GET, SHARE, LOGIN, DATA')
        2. user: user name
        3. parameters: hold query parametes in dictionary
    """
    def __init__(self, command, user, parameters):
        """
        initlilize class menbers

        Args:
            1. command: query command
            2. uer: user name
            3. parameters: query fields
        """
        self.command = command
        self.user = user
        self.parameters = parameters

    def get_command(self):
        """
        getter for command field

        Returns:
            command: query command
        """
        return self.command

    def get_user(self):
        """
        getter for uesr field

        Returns:
            user: username
        """
        return self.user

    def get_parameters(self):
        """
        getter for parameters

        Returns:
            parameters: query parameters (dictionary)
        """
        return self.parameters

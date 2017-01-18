class FloydException(Exception):

    def __init__(self,
                 message=None,
                 status_code=None):
        self.message = message
        self.status_code = status_code
        super(FloydException, self).__init__(message)


class AuthenticationException(FloydException):

    def __init__(self,
                 message="Authentication Failed",
                 status_code=401):
        super(AuthenticationException, self).__init__(message=message,
                                                      status_code=status_code)

from click import ClickException


class FloydException(ClickException):

    def __init__(self, message=None, code=None):
        super(FloydException, self).__init__(message)


class AuthenticationException(ClickException):

    def __init__(self, message="Authentication failed. Retry by invoking floyd login."):
        super(AuthenticationException, self).__init__(message=message)


class NotFoundException(ClickException):

    def __init__(self, message="The resource you are looking for is not found. Check if the id is correct."):
        super(NotFoundException, self).__init__(message=message)


class BadRequestException(ClickException):

    def __init__(self, message="One or more request parameter is incorrect."):
        super(BadRequestException, self).__init__(message=message)


class OverLimitException(ClickException):

    def __init__(self, message="You are over the allowed limits for this operation. Consider upgrading your account."):
        super(OverLimitException, self).__init__(message=message)

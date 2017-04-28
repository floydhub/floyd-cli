from click import ClickException


class FloydException(ClickException):

    def __init__(self, message=None, code=None):
        super(FloydException, self).__init__(message)


class AuthenticationException(FloydException):

    def __init__(self, message="Authentication failed. Retry by invoking floyd login."):
        super(AuthenticationException, self).__init__(message=message)


class AuthorizationException(FloydException):

    def __init__(self, message="You are not authorized to access this resource on FloydHub."):
        super(AuthorizationException, self).__init__(message=message)


class NotFoundException(FloydException):

    def __init__(self, message="The resource you are looking for was not found. Check if the id is correct."):
        super(NotFoundException, self).__init__(message=message)


class BadRequestException(FloydException):

    def __init__(self, message="One or more request parameters is incorrect."):
        super(BadRequestException, self).__init__(message=message)


class OverLimitException(FloydException):

    def __init__(self, message="You are over the allowed limits for this operation. Consider upgrading your account."):
        super(OverLimitException, self).__init__(message=message)


class ServerException(FloydException):

    def __init__(self, message="Internal FloydHub server error."):
        super(ServerException, self).__init__(message=message)


class BadGatewayException(FloydException):

    def __init__(self, message="Invalid response from FloydHub server."):
        super(BadGatewayException, self).__init__(message=message)


class GatewayTimeoutException(FloydException):

    def __init__(self, message="FloydHub server took too long to respond."):
        super(GatewayTimeoutException, self).__init__(message=message)

class LoginFailedError(BaseException):

    def __init__(self):
        super(LoginFailedError, self).__init__()
        
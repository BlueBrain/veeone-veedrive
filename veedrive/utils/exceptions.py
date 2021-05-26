class CodeException(Exception):
    def __init__(self, code, message=""):
        super().__init__(message)
        self.code = code


class WrongObjectType(Exception):
    pass

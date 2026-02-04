class ApplicationError(Exception):
    pass


class NotFoundError(ApplicationError):
    pass


from domain.exceptions import DuplicateEmailError


class DatabaseError(ApplicationError):
    pass

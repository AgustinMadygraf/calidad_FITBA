class ApplicationError(Exception):
    pass


class NotFoundError(ApplicationError):
    pass

class DatabaseError(ApplicationError):
    pass

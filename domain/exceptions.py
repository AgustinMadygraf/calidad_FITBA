class DomainError(Exception):
    pass


class ValidationError(DomainError):
    pass


class DuplicateEmailError(DomainError):
    pass

from abc import ABC, abstractmethod
from domain.repositories.contact_repository import IContactRepository


class IUnitOfWork(ABC):
    contacts: IContactRepository

    @abstractmethod
    def __enter__(self) -> "IUnitOfWork": ...

    @abstractmethod
    def __exit__(self, exc_type, exc, tb) -> None: ...

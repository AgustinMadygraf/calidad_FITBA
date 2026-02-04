from abc import ABC, abstractmethod
from domain.entities.contact import Contact


class IContactRepository(ABC):
    @abstractmethod
    def create(self, contact: Contact) -> Contact: ...

    @abstractmethod
    def update(self, contact: Contact) -> Contact: ...

    @abstractmethod
    def delete(self, contact_id: int) -> None: ...

    @abstractmethod
    def get_by_id(self, contact_id: int) -> Contact | None: ...

    @abstractmethod
    def search(self, query: str, limit: int, offset: int) -> list[Contact]: ...

    @abstractmethod
    def list(self, limit: int, offset: int) -> list[Contact]: ...

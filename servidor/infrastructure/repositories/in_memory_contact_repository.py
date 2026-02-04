from domain.entities.contact import Contact
from domain.repositories.contact_repository import IContactRepository
from domain.exceptions import DuplicateEmailError


class InMemoryContactRepository(IContactRepository):
    def __init__(self) -> None:
        self._data: dict[int, Contact] = {}
        self._seq = 1

    def create(self, contact: Contact) -> Contact:
        if contact.email and self._email_exists(contact.email.value):
            raise DuplicateEmailError("Email duplicado")
        contact.id = self._seq
        self._seq += 1
        self._data[contact.id] = contact
        return contact

    def update(self, contact: Contact) -> Contact:
        if contact.email and self._email_exists(contact.email.value, exclude_id=contact.id):
            raise DuplicateEmailError("Email duplicado")
        if not contact.id:
            raise ValueError("ID requerido")
        self._data[contact.id] = contact
        return contact

    def delete(self, contact_id: int) -> None:
        if contact_id in self._data:
            del self._data[contact_id]

    def get_by_id(self, contact_id: int) -> Contact | None:
        return self._data.get(contact_id)

    def search(self, query: str, limit: int, offset: int) -> list[Contact]:
        q = query.lower()
        results = [
            c
            for c in self._data.values()
            if q in c.full_name.lower()
            or (c.email and q in c.email.value.lower())
            or (c.phone and q in c.phone.value.lower())
        ]
        results.sort(key=lambda c: c.id or 0, reverse=True)
        return results[offset : offset + limit]

    def list(self, limit: int, offset: int) -> list[Contact]:
        results = list(self._data.values())
        results.sort(key=lambda c: c.id or 0, reverse=True)
        return results[offset : offset + limit]

    def _email_exists(self, email: str, exclude_id: int | None = None) -> bool:
        for c in self._data.values():
            if c.email and c.email.value == email:
                if exclude_id is None or c.id != exclude_id:
                    return True
        return False

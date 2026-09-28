"""Bind authenticated channel identities; this module does not authenticate them."""

from dataclasses import dataclass
from collections.abc import Iterable
from types import MappingProxyType


class Denied(PermissionError):
    """The supplied context does not match an authorized binding."""


def _valid_id(value: object) -> bool:
    return isinstance(value, str) and bool(value) and value.strip() == value


@dataclass(frozen=True)
class Binding:
    principal: str
    user: str
    chat: str


class Registry:
    """Immutable one-to-one synthetic private-channel registry.

    The caller must obtain user/chat from a verified channel event, never
    from a prompt or client-selected principal. No fuzzy matching is used.
    """

    def __init__(self, bindings: Iterable[Binding]) -> None:
        pairs: dict[tuple[str, str], str] = {}
        principals: set[str] = set()
        users: set[str] = set()
        chats: set[str] = set()
        for binding in bindings:
            if not all(_valid_id(x) for x in (binding.principal, binding.user, binding.chat)):
                raise ValueError("Invalid binding configuration")
            if binding.principal in principals or binding.user in users or binding.chat in chats:
                raise ValueError("Ambiguous binding configuration")
            principals.add(binding.principal)
            users.add(binding.user)
            chats.add(binding.chat)
            pairs[binding.user, binding.chat] = binding.principal
        self._pairs = MappingProxyType(pairs)

    def resolve(self, user: object, chat: object, kind: object) -> str:
        if kind != "private" or not _valid_id(user) or not _valid_id(chat):
            raise Denied("Channel binding denied")
        principal = self._pairs.get((user, chat))
        if principal is None:
            raise Denied("Channel binding denied")
        return principal

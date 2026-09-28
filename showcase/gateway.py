"""Bounded fallback over trusted, operator-configured provider adapters."""

import asyncio
import math
from dataclasses import dataclass
from typing import Protocol

from showcase.identity import Denied


class Provider(Protocol):
    async def complete(self, prompt: str) -> str: ...


class ProviderFailure(Exception):
    """A status classified by a trusted adapter, never by generated text."""

    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__("Provider request failed")


@dataclass(frozen=True)
class Route:
    owner: str
    name: str
    provider: Provider


@dataclass(frozen=True)
class Completion:
    text: str
    route: str
    attempts: int


class Gateway:
    """No credentials, environment lookup, networking or route discovery.

    Principal and routes are trusted application inputs, not an HTTP API.
    Timeouts require cooperative asynchronous adapters. This is not a process
    execution boundary and cannot stop blocking or malicious provider code.
    """

    def __init__(self, timeout: float = 1.0) -> None:
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Timeout must be positive and finite")
        self._timeout = timeout

    async def _call(self, route: Route, prompt: str) -> str:
        async with asyncio.timeout(self._timeout):
            return await route.provider.complete(prompt)

    async def complete(
        self, principal: str, prompt: str, primary: Route,
        fallback: Route | None = None,
    ) -> Completion:
        if not isinstance(principal, str) or not principal or principal.strip() != principal:
            raise Denied("Provider ownership denied")
        routes = (primary,) if fallback is None else (primary, fallback)
        if any(route.owner != principal for route in routes):
            raise Denied("Provider ownership denied")
        if fallback is not None and primary.name == fallback.name:
            raise ValueError("Fallback must be a distinct route")
        try:
            text = await self._call(primary, prompt)
        except ProviderFailure as failure:
            if failure.status not in (402, 429) or fallback is None:
                raise
        else:
            return Completion(text, primary.name, 1)
        # Outside the handler: a fallback failure propagates; it cannot recurse.
        text = await self._call(fallback, prompt)
        return Completion(text, fallback.name, 2)

"""Run with python -m showcase.demo; all identities and responses are synthetic."""

import asyncio
import json
from dataclasses import asdict

from showcase.gateway import Gateway, ProviderFailure, Route
from showcase.identity import Binding, Denied, Registry


class FakeProvider:
    """A deterministic fixture, not an LLM or a network adapter."""

    def __init__(self, status: int = 200) -> None:
        self.status = status

    async def complete(self, prompt: str) -> str:
        if self.status != 200:
            raise ProviderFailure(self.status)
        return "Synthetic response: " + prompt


class MustNotRun:
    async def complete(self, prompt: str) -> str:
        raise AssertionError("Unauthorized provider was called")


async def scenario() -> dict[str, object]:
    registry = Registry((Binding("principal-a", "user-a", "chat-a"),
                         Binding("principal-b", "user-b", "chat-b")))
    principal = registry.resolve("user-a", "chat-a", "private")
    try:
        registry.resolve("user-a", "chat-b", "private")
    except Denied:
        crossed = "denied"
    else:
        raise AssertionError("Crossed identity unexpectedly allowed")

    gateway = Gateway()
    primary = await gateway.complete(
        principal, "hello", Route(principal, "synthetic-primary", FakeProvider()))
    fallback = await gateway.complete(
        principal, "hello", Route(principal, "synthetic-primary", FakeProvider(429)),
        Route(principal, "synthetic-backup", FakeProvider()))
    try:
        await gateway.complete(
            principal, "hello", Route(principal, "synthetic-primary", MustNotRun()),
            Route("principal-b", "foreign-backup", MustNotRun()))
    except Denied:
        foreign = "denied-before-provider-call"
    else:
        raise AssertionError("Foreign provider unexpectedly allowed")
    return {
        "mode": "offline-simulation", "principal": principal,
        "crossed_pair": crossed, "primary": asdict(primary),
        "quota_fallback": asdict(fallback), "foreign_owner": foreign,
    }


if __name__ == "__main__":
    print(json.dumps(asyncio.run(scenario()), indent=2, sort_keys=True))

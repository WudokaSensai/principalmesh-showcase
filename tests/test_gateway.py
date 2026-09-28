import asyncio

import pytest

from showcase.gateway import Gateway, ProviderFailure, Route
from showcase.identity import Denied


class Stub:
    def __init__(self, result="ok", error=None):
        self.result, self.error = result, error
        self.calls = []

    async def complete(self, prompt):
        self.calls.append(prompt)
        if self.error is not None:
            raise self.error
        return self.result


def route(provider, name="primary", owner="principal-a"):
    return Route(owner, name, provider)


def run(primary, fallback=None, principal="principal-a"):
    return asyncio.run(Gateway().complete(principal, "synthetic prompt", primary, fallback))


def test_primary_success_does_not_call_fallback():
    primary, fallback = Stub("primary answer"), Stub("fallback answer")
    result = run(route(primary), route(fallback, "fallback"))
    assert (result.text, result.route, result.attempts) == ("primary answer", "primary", 1)
    assert fallback.calls == []


@pytest.mark.parametrize("status", [402, 429])
def test_quota_failure_uses_one_fallback(status):
    primary, fallback = Stub(error=ProviderFailure(status)), Stub("fallback answer")
    result = run(route(primary), route(fallback, "fallback"))
    assert (result.text, result.route, result.attempts) == ("fallback answer", "fallback", 2)
    assert primary.calls == fallback.calls == ["synthetic prompt"]


@pytest.mark.parametrize("status", [400, 401, 403, 404, 408, 500, 503])
def test_other_provider_failures_do_not_fallback(status):
    fallback = Stub()
    with pytest.raises(ProviderFailure) as caught:
        run(route(Stub(error=ProviderFailure(status))), route(fallback, "fallback"))
    assert caught.value.status == status
    assert fallback.calls == []


@pytest.mark.parametrize("error", [OSError("offline"), asyncio.CancelledError()])
def test_transport_errors_and_cancellation_propagate(error):
    fallback = Stub()
    with pytest.raises(type(error)):
        run(route(Stub(error=error)), route(fallback, "fallback"))
    assert fallback.calls == []


def test_fallback_failure_does_not_retry():
    primary, fallback = Stub(error=ProviderFailure(429)), Stub(error=ProviderFailure(429))
    with pytest.raises(ProviderFailure):
        run(route(primary), route(fallback, "fallback"))
    assert len(primary.calls) == len(fallback.calls) == 1


def test_quota_failure_without_fallback_propagates():
    with pytest.raises(ProviderFailure):
        run(route(Stub(error=ProviderFailure(402))))


@pytest.mark.parametrize("primary_owner,fallback_owner", [
    ("principal-b", "principal-a"), ("principal-a", "principal-b")])
def test_both_routes_authorized_before_io(primary_owner, fallback_owner):
    primary, fallback = Stub(), Stub()
    with pytest.raises(Denied):
        run(route(primary, owner=primary_owner), route(fallback, "fallback", fallback_owner))
    assert primary.calls == fallback.calls == []


def test_same_route_cannot_be_its_own_fallback():
    primary = Stub()
    with pytest.raises(ValueError):
        run(route(primary), route(primary))
    assert primary.calls == []


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), True, "1"])
def test_invalid_timeout_rejected(timeout):
    with pytest.raises(ValueError):
        Gateway(timeout=timeout)


@pytest.mark.parametrize("principal", ["", " principal-a", None, True])
def test_invalid_principal_denied(principal):
    primary = Stub()
    with pytest.raises(Denied):
        run(route(primary), principal=principal)
    assert primary.calls == []


def test_timeout_does_not_trigger_fallback():
    class Slow:
        async def complete(self, prompt):
            await asyncio.sleep(10)
            return "late"
    fallback = Stub()
    with pytest.raises(TimeoutError):
        asyncio.run(Gateway(timeout=0.01).complete(
            "principal-a", "prompt", route(Slow()), route(fallback, "fallback")))
    assert fallback.calls == []


def test_concurrent_requests_do_not_mix_routes():
    class Echo:
        async def complete(self, prompt):
            await asyncio.sleep(0)
            return prompt
    async def scenario():
        gateway = Gateway()
        return await asyncio.gather(*(
            gateway.complete(f"principal-{i}", f"prompt-{i}",
                             Route(f"principal-{i}", f"route-{i}", Echo()))
            for i in range(20)))
    results = asyncio.run(scenario())
    assert [(r.text, r.route) for r in results] == [(f"prompt-{i}", f"route-{i}") for i in range(20)]


@pytest.mark.parametrize("cancel_backup", [False, True])
def test_cancelling_in_flight_request_propagates_without_retry(cancel_backup):
    async def scenario():
        started = asyncio.Event()
        stopped = asyncio.Event()
        calls = []

        class Waiting:
            async def complete(self, prompt):
                calls.append(prompt)
                started.set()
                try:
                    await asyncio.Event().wait()
                finally:
                    stopped.set()

        backup = Stub()
        primary = Stub(error=ProviderFailure(429)) if cancel_backup else Waiting()
        fallback = Waiting() if cancel_backup else backup
        task = asyncio.create_task(Gateway(timeout=5).complete(
            "principal-a", "prompt", route(primary), route(fallback, "fallback")))
        try:
            await asyncio.wait_for(started.wait(), timeout=1)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, timeout=1)
            assert stopped.is_set()
            assert calls == ["prompt"]
            if cancel_backup:
                assert primary.calls == ["prompt"]
            else:
                assert backup.calls == []
        finally:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    asyncio.run(scenario())

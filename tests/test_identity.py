import pytest

from showcase.identity import Binding, Denied, Registry


def registry():
    return Registry((Binding("principal-a", "user-a", "chat-a"),
                     Binding("principal-b", "user-b", "chat-b")))


@pytest.mark.parametrize("suffix", ["a", "b"])
def test_exact_binding(suffix):
    assert registry().resolve(f"user-{suffix}", f"chat-{suffix}", "private") == f"principal-{suffix}"


@pytest.mark.parametrize("user,chat,kind", [
    ("user-a", "chat-b", "private"), ("user-b", "chat-a", "private"),
    ("unknown", "chat-a", "private"), ("user-a", "chat-a", "group"),
    ("user-a", "chat-a", "PRIVATE"), ("", "chat-a", "private"),
    (None, "chat-a", "private"), ([], "chat-a", "private"),
    (True, "chat-a", "private"), (" user-a", "chat-a", "private"),
])
def test_untrusted_pairs_are_denied(user, chat, kind):
    with pytest.raises(Denied):
        registry().resolve(user, chat, kind)


@pytest.mark.parametrize("second", [
    Binding("principal-b", "user-a", "chat-b"),
    Binding("principal-b", "user-b", "chat-a"),
    Binding("principal-a", "user-b", "chat-b"),
    Binding("principal-a", "user-a", "chat-a"),
])
def test_ambiguous_configuration_rejected(second):
    with pytest.raises(ValueError):
        Registry((Binding("principal-a", "user-a", "chat-a"), second))


@pytest.mark.parametrize("value", ["", " ", " principal-a", None, True, []])
def test_invalid_configuration_rejected(value):
    with pytest.raises(ValueError):
        Registry((Binding(value, "user-a", "chat-a"),))


def test_registry_snapshots_input():
    bindings = [Binding("principal-a", "user-a", "chat-a")]
    subject = Registry(bindings)
    bindings.clear()
    assert subject.resolve("user-a", "chat-a", "private") == "principal-a"


def test_empty_registry_denies():
    with pytest.raises(Denied):
        Registry(()).resolve("user-a", "chat-a", "private")

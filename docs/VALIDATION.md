# Validation

Local verification: 2026-09-27, Linux, Python 3.12.14, pytest 9.1.1.

| Check | Result |
| --- | --- |
| `python -m pytest -q` | 56 passed |
| Same suite with IPv4/IPv6 socket creation denied | 56 passed |
| `python -m showcase.demo` | Exit 0; deterministic synthetic JSON |
| `python -m compileall -q showcase tests` | Exit 0 |
| `git diff --check` | Exit 0 |

Coverage includes exact and crossed identity pairs, duplicate configuration,
provider ownership before I/O, quota-only fallback, transport failures,
cooperative timeouts, cancellation of active primary and backup calls, and
20 interleaved requests with distinct results.

The network-restricted run used a Linux seccomp launcher that denied new IPv4
and IPv6 sockets before launching pytest, including its demo subprocess. Local
Unix socket pairs remained allowed. This is validation of exercised offline
paths, not a sandbox feature or a hostile-code isolation guarantee.

[GitHub Actions](../.github/workflows/tests.yml) is configured to run tests,
demo and compilation on Python 3.11 and 3.12. No successful hosted CI run is
claimed until one appears on GitHub. Installing test dependencies needs package
access; the demo itself uses only the Python standard library.

No real credentials, LLM providers, database, live channel, persistent memory,
sandbox or private-platform tests were exercised. Windows was not tested.

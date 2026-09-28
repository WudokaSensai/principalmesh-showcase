# PrincipalMesh · Engineering Showcase

**AI / Backend Engineering · Python · Identity boundaries · Provider routing**

An offline, runnable portfolio by **[WudokaSensai](https://github.com/WudokaSensai)**.
It demonstrates two engineering decisions from the PrincipalMesh project through
small, independently rewritten examples. The full platform remains private.

> **The original PrincipalMesh is substantially more advanced than this showcase.**
> It is a broader private multi-principal AI platform. This repository deliberately
> exposes only two rewritten policy examples with synthetic data; its size and
> feature set do **not** represent the full project's scope.

## Private platform vs. public excerpt

The original project spans an authenticated backend, persistent data and memory,
provider integrations, user interfaces and controlled execution. This excerpt
keeps the review surface small so a recruiter can run and inspect it quickly.

| Area | Private PrincipalMesh scope | Demonstrated here |
| --- | --- | --- |
| Backend and identity | FastAPI API, authentication and scoped service accounts | Exact synthetic user/chat binding |
| Data and memory | PostgreSQL/pgvector storage, conversations and ownership-scoped memory code | No database or persistent memory |
| Model access | Provider adapters, ownership checks and configured routing | Fake providers and one bounded fallback |
| Interfaces | Next.js console and Telegram integration | Offline command-line demo |
| Controlled execution | Rootless Podman execution path and sandbox-related tests | No command execution; contract described only |

**This is a focused engineering sample from a larger project, not the platform's
complete implementation.** The private scope above describes repository
components; public tests validate only this excerpt. Broader scope is not a claim
of production readiness, certification or independent security verification.

## The problem

An AI application must not let a message choose another user's identity or let
a fallback provider quietly expand access. These boundaries belong in application
code, outside generated text.

This repository makes those decisions easy to inspect: resolve an exact channel
identity, check provider ownership, and attempt one explicitly configured backup
only for quota failures. Invalid identity and ownership checks deny access.

## Run in 30 seconds

Requires **Python 3.11+**. Run from the repository root; runtime uses only the
standard library. No API keys, account, containers or network calls are needed.

```bash
python -m showcase.demo
```

The JSON output reports:

| Scenario | Expected result |
| --- | --- |
| Exact synthetic user/chat binding | `principal-a` |
| Crossed user/chat pair | `denied` |
| Primary succeeds | One attempt |
| Primary returns simulated 429 | One backup attempt; two total |
| Backup belongs to another principal | Denied before any provider call |

For tests, create a virtual environment and install the test dependency
(installation needs package access; running tests does not):

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install "pytest>=8,<10"
python -m pytest -q
```

## What to review

| Example | Implementation | Evidence |
| --- | --- | --- |
| Exact binding, fail-closed configuration | [identity.py](showcase/identity.py) | [Identity tests](tests/test_identity.py) |
| Owner checks before I/O; one quota fallback | [gateway.py](showcase/gateway.py) | [Gateway tests](tests/test_gateway.py) |
| Deterministic, synthetic end-to-end flow | [demo.py](showcase/demo.py) | [Demo test](tests/test_demo.py) |

Tests cover crossed pairs, unknown identities, duplicate bindings, foreign
providers, non-quota errors, cancellation, timeouts and concurrent requests.
See [validation](docs/VALIDATION.md) for the actual run and its limits.

## My contribution and project context

I built PrincipalMesh as an independent AI/backend platform project, focusing on
principal-scoped access, provider routing and controlled execution. Its broader
technology stack includes FastAPI, PostgreSQL/pgvector, Redis, Next.js and rootless
Podman. Those systems are **not bundled or exercised by this showcase**.

This public edition translates two design choices into readable Python examples
and executable tests. AI coding tools assisted with implementation and review;
the examples are intended for technical discussion, not as proof of unaided work.

## Scope and honesty

| Working here | Simulated | Not included |
| --- | --- | --- |
| Exact identity matching and owner checks | Channel identities | Authentication server or Telegram integration |
| Bounded asynchronous fallback policy | Provider responses and status codes | Real LLM calls or production failover |
| Regression tests and deterministic demo | In-memory configuration | Database, persistent memory or tenant isolation |
| Per-call cooperative timeout | Provider latency in tests | Sandbox execution, agent autonomy or deployment |

The gateway accepts **trusted application objects**, not user-submitted routes.
Identity binding is not authentication. This demo does not establish memory
isolation, provide a sandbox, or claim production readiness.

Read [architecture and trade-offs](docs/ARCHITECTURE.md) for the trust boundary,
[CV wording](docs/CV.md) for a concise project description, and
[review](docs/REVIEW.md) for remaining limitations.

## License

[MIT](LICENSE) applies only to the newly written material in this repository.
No private PrincipalMesh source, assets or commercial rights are granted.

# Scope and limitations

This repository is a small, independently rewritten portfolio excerpt. It is
suitable for reviewing identity and routing policy, not for deployment as a
complete AI service.

- Principal and route objects come from trusted application code. Authentication
  and server-side route storage would be required at an HTTP boundary.
- There is no persistent memory, organization model, sandbox or live provider.
- Timeouts require cooperative asynchronous adapters; they cannot stop blocking
  or malicious code.
- Tests cover this excerpt, not the private PrincipalMesh platform.
- Linux/Python 3.12 has been exercised locally. CI targets Python 3.11 and 3.12;
  compatibility on unexecuted environments is not claimed.
- Test dependencies use a bounded version range rather than a lockfile.

An independent review of the initial 54-test version found no critical, high or
medium issues within this scope. Its cancellation coverage suggestion is now
addressed by tests that cancel active primary and backup calls. The updated
suite has 56 tests. Code review and passing tests are not a security audit.

---
status: draft
size: L
scope: PDOC-20
owner: ginb
---
# Plan — PDOC-20

1. Tests first: builder semantic sections, normalization, hash stability, unknown provider, incomplete package.
2. Implement `provider_document.py` (local renderer private).
3. Local adapter + collision tests (write, adopt, conflict-block).
4. Extend `validate_package` for document reference; keep legacy path green.
5. Concise cards linking the document; card test asserts no Contract/Spec/Plan body duplication.
6. Gate: `document_baseline` validation + drift/uncommitted rejection tests.
7. Extend lifecycle test; wire new tests into `Makefile` (`core-test`, `plugin-test`).
8. `make lint && make test`; mark docs completed; commit scoped files.

Risks: touching `execution_package.py` and `card_creation.py` overlaps #22/#23; keep reference shape provider-neutral now.

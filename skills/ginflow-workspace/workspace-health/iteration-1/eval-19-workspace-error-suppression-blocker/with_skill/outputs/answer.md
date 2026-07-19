Workspace warnings:
- blocker: changed payment-capture path uses `except Exception: pass` and records invoice as paid after charge failure — silent payment failure can corrupt invoice state and violates data integrity; next: propagate or handle charge errors explicitly, record paid status only after confirmed capture, add failure-path coverage, then rerun canonical verification.

Completion readiness: blocked despite passing tests.

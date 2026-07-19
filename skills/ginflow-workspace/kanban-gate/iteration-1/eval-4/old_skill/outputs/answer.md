# No-card gate decision

**Decision: Do not start implementation.**

Ginflow requires one active selected or assigned Kanban card per worker. Project startup also requires reading that card and confirming objective, scope, acceptance criteria, and workspace before repository inspection or changes. Clear, small bug does not waive card gate.

**Next action:** Ask Gin to select or assign Kanban card for `/work/app`. Card must identify objective, bounded scope, acceptance criteria, key exclusions, and real workspace. After selection, read card and linked artifacts plus `/work/app` local rules, confirm inputs, inspect git state, run baseline verification, then start implementation.

No `/work/app` files may be edited before gate passes.

# Choose feedback contract ownership boundary

## Question

Should the normalized lifecycle feedback event contract remain owned by `ginflow-gate`, or should it live in reusable Ginflow core policy while the plugin only adapts events and injects guidance?

The decision must preserve purity, existing blocker/recovery boundaries, non-mutation, supported signal mappings, and the out-of-scope boundary against telemetry and full orchestration.

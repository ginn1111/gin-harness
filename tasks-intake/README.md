# TASKS INTAKE JUST FOR HUMANS NOTE TASKS

---

- [ ] [Workspace setup]: Do not hard the verify canonial scripts, workspace-detect. Should define the from ginflow skills

- [ ] [Workspace workflow]: Now the card is done, but the briefs is active. This is violate the consistency?

- [ ] Convert ginflow skills to the hermes skill format

- [ ] [Workspace workflow]: When I mention ginflow, agents do not try to read the current progress:
  - If there are no kanban cards -> routing to work routing sizing
  - If there are kanban cards -> use hermes kanban tools to understand the progress first, after that continue process
- Let's try to plugin hook approach:
  - Inject in the pre_llm_call hook, if the active skills contain ginflow, we should inject the ginflow-routing sub skills to guide the agent

- [ ] [Workspace specs]: When I invoke ginflow, when the agents routing task sizing -> start brainstorming with and write specs, need to the human review before run!
  - Let's try approach, because the user invoke skills immediately, you should refer the ginflow-routing already in SKILLS.md


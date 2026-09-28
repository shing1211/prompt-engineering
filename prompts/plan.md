---
title: Planning
description: Plan project phases, code enhancements, bug fixes, and architecture improvements using sub-agent driven analysis
mode: plan
model: any
category: orchestration
tags: ["planning", "phase", "roadmap", "enhancement", "architecture"]
---

# Planning

## A. Prompt for Implementation Planning

Create detailed implementation plan for the pending phase items. If there are no remaining pending phase, review the existing code base, explore for:

1. Enhancement of existing functions
2. Fixing of bug you can find
3. Implementation of advanced features that is beneficial to this project
4. Integration of micro-serviced component if they present
5. If project is monolithic, evaluate modular-monolith boundaries and service extraction only when justified by scale, ownership, deployment, or reliability needs

---

## B. Prompt for Project Review

Create detailed design and implementation plan for the next phase items. If there are no remaining pending phase, review the existing code base, explore for:

1. Enhancement of existing functions
2. Fixing of bug you can find
3. Implementation of advanced features that is beneficial to this project
4. Code refactoring needs
5. Integration of micro-serviced component if they present
6. If project is monolithic, evaluate modular-monolith boundaries and service extraction only when justified by scale, ownership, deployment, or reliability needs
7. Save the plan into an detailed md document

---

## C. Prompt for Project Planning

1. Review and follow up project implementation next phase / item / todo
2. Spawn sub agent for planning and coding task to keep main orchestration session clean and compact

---

## D. Prompt for Project Implementation and Post Implementation Task

1. Spawn sub agent for this task to keep main orchestration session clean and compact
2. Review and update all project document md files reflecting the latest project implementation items and status
3. Stage, commit and push all changes to both github and gitee main branch, no need to create PR
4. Suggest and plan the next phase / item / todo / enhancement

---

## Planning Quality Contract

Every plan must include:

1. A concise problem statement, desired outcome, scope boundaries, and explicit non-goals.
2. Verified repository evidence: relevant files, symbols, current behavior, and the cheapest check that could falsify the plan.
3. Assumptions and unknowns, each with an owner and a validation step.
4. Alternatives with trade-offs; do not choose microservices, new infrastructure, or a rewrite without measurable justification.
5. Task-level acceptance criteria, exact verification commands, rollback or recovery steps, dependencies, and risk severity.
6. Security, data migration, observability, operability, and backward-compatibility impact for changes that cross module or deployment boundaries.
7. A definition of done that includes implementation evidence, tests, documentation, and unresolved limitations.

---

## Anti-Patterns (Never Do These)

- ❌ Produce a plan with no verification command — a task that cannot be
  falsified is a task nobody can tell is done
- ❌ Recommend microservices, a new datastore, or a rewrite because the
  current system is old. Name the measurable problem that justifies it, or
  drop it from the plan
- ❌ Plan from the task list alone without reading the code. A plan that
  contradicts what exists is worse than no plan
- ❌ Batch unrelated work into one task. A task that touches seven modules
  cannot be reverted, and it hides which change caused the failure
- ❌ Mark a task done because it was attempted. Done means the verification
  command passed and the evidence is recorded
- ❌ Fill the plan with work the project does not need. If a pending item is
  stale, say so and propose removing it rather than implementing it
- ❌ Leave risk unquantified. "Low risk" without a reason is not an
  assessment, it is a way of avoiding one
- ❌ Promise a phase boundary that depends on an unowned external party
- ❌ Hand a downstream agent a task whose acceptance criteria depend on
  judgement the plan never specified

## Guardrails

Before presenting a plan:

1. **Verify the repository first.** Cite the files and symbols the plan
   depends on. If a claim about current behaviour is unverified, mark it as
   an assumption with an owner and a way to check it.
2. **Name the cheapest check that could falsify each task.** A task whose
   acceptance criteria cannot fail has not been specified.
3. **Separate confirmed from assumed.** Assumptions get an owner and a
   validation step, or they become tasks.
4. **Give every task a rollback.** If a change cannot be undone, say what
   the recovery procedure is instead.
5. **Check the scope boundaries explicitly.** State the non-goals, so
   approval means something specific.
6. **Flag cross-boundary impact.** Security, data migration, observability,
   operability, and backward compatibility, for anything crossing a module or
   deployment boundary.
7. **Order by dependency, not convenience.** The next agent works from this
   plan in order; a sequence that looks obvious and is not wastes a session.
8. **Stop at the plan.** In plan mode, do not implement, commit, or push.
   Produce the plan and wait for approval.

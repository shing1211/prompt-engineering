---
title: Planning
description: Plan project phases, code enhancements, bug fixes, and architecture improvements using sub-agent driven analysis
mode: plan
model: any
category: orchestration
tags: ["planning", "phase", "roadmap", "enhancement", "architecture"]
---

# Planning Prompts

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

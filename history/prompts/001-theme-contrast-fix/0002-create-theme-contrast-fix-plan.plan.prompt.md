---
id: 0002
title: Create theme contrast fix plan
stage: plan
date: 2026-02-16
surface: agent
model: claude-sonnet-4-5
feature: 001-theme-contrast-fix
branch: 001-theme-contrast-fix
user: user
command: /sp.plan
labels: ["plan", "accessibility", "theme", "dark-mode", "wcag", "frontend", "contrast"]
links:
  spec: ../../specs/001-theme-contrast-fix/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-theme-contrast-fix/plan.md
  - specs/001-theme-contrast-fix/research.md
  - specs/001-theme-contrast-fix/quickstart.md
tests:
  - Constitution Check (all gates passed with scope clarification needed)
---

## Prompt

```text
sp.plan: Frontend Theme Update Implementation
Phase 1: Audit & Analysis

Audit current frontend theme:

Extract all colors used for text, backgrounds, buttons, links, headings

Identify contrast issues in dark mode and light mode

Check against WCAG 2.1 contrast guidelines:

Normal text: ≥ 4.5:1

Large text: ≥ 3:1

Phase 2: Theme Fix Implementation

Dark Mode:

Update text colors to lighter shades (e.g., #FFFFFF, #F0F0F0)

Ensure background and UI components have sufficient contrast

Light Mode:

Update text colors to darker shades (e.g., #000000, #111111)

Verify buttons, links, headings contrast well against background

Update CSS variables or frontend theme configuration

Consider using a design system or Tailwind/Material theme for consistency

Phase 3: Testing

Test all components (headings, paragraphs, buttons, links) in both dark and light modes

Automated contrast checking (optional: use tools like axe-core or Lighthouse)

Manual visual verification

Phase 4: Deployment

Apply updated theme to frontend
```

## Response snapshot

**Critical Discovery**: Research revealed that dark mode does not currently exist in the application. This changes the feature scope from "fixing contrast in both modes" to "implementing dark mode + ensuring proper contrast."

**Phase 0 Research Completed**:
- Explored current theme implementation (CSS variables in globals.css)
- Audited existing colors and contrast ratios
- Found light mode already meets WCAG 2.1 AA standards (all elements pass)
- Identified inconsistency: Button component uses hardcoded colors instead of CSS variables
- Researched WCAG 2.1 standards and accessibility testing tools
- Proposed dark mode color palette with validated contrast ratios

**Phase 1 Design Completed**:
- Created comprehensive implementation plan with technical context
- Documented 5 research tasks with clear goals and outputs
- Created quickstart.md with testing procedures and validation checklists
- Proposed class-based dark mode with system preference default
- Defined success metrics and validation methods

**Constitution Re-Evaluation**: All gates passed with note that scope expansion (dark mode implementation) should be communicated to stakeholders.

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation. Identified critical scope expansion that requires stakeholder awareness.
- 🧪 Tests: Constitution Check passed (5/5 principles), testing strategy documented in quickstart.md
- 📁 Files: 3 files created (plan.md, research.md, quickstart.md)
- 🔁 Next prompts: `/sp.tasks` to generate detailed task breakdown, or clarify scope expansion with stakeholders first
- 🧠 Reflection: Research phase uncovered significant assumption gap (dark mode existence). This demonstrates value of thorough discovery before implementation. The spec assumed dark mode existed, but it doesn't - highlighting importance of validating assumptions early.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning workflow executed successfully. However, spec made incorrect assumption about dark mode existence, which was caught during research phase.
- Graders run and results (PASS/FAIL): Constitution Check - PASS (5/5 principles with scope clarification note)
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 research and Phase 1 design
- Next experiment (smallest change to try): Consider adding "current state validation" step to spec workflow to catch assumption gaps earlier

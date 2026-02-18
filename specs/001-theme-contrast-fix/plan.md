# Implementation Plan: Frontend Theme Contrast Fix

**Branch**: `001-theme-contrast-fix` | **Date**: 2026-02-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-theme-contrast-fix/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix text contrast issues in the frontend theme to meet WCAG 2.1 Level AA accessibility standards. Adjust colors for headings, paragraphs, buttons, and links in both light and dark modes to ensure all text elements have sufficient contrast ratios (4.5:1 for normal text, 3:1 for large text). This is a frontend-only change that modifies the visual presentation layer without affecting functionality or data.

## Technical Context

**Language/Version**: TypeScript 5.0+ / JavaScript ES6+, Node.js 18+
**Primary Dependencies**: Next.js 16+ (App Router), React 18+, TailwindCSS (assumed based on modern Next.js stack)
**Storage**: N/A (no data storage required)
**Testing**: Visual testing, accessibility audit tools (axe-core, Lighthouse), manual testing across browsers
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) on desktop and mobile
**Project Type**: Web (frontend only)
**Performance Goals**: Instant theme switching (<50ms), no impact on page load times
**Constraints**: WCAG 2.1 Level AA compliance (4.5:1 contrast for normal text, 3:1 for large text), maintain visual aesthetics
**Scale/Scope**: All existing pages and components in the frontend application

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Pre-Research)

### Principle I: Functional Correctness Across All Layers
✅ **PASS** - Theme changes must render correctly across all components and pages. All text must be readable in both light and dark modes. Testing will verify correct rendering and contrast ratios.

### Principle II: Security-First Design
✅ **N/A** - This feature only modifies CSS/styling and does not involve authentication, authorization, or data handling. No security implications.

### Principle III: Clear Separation of Concerns
✅ **PASS** - This is a frontend-only change affecting the presentation layer. No backend or database modifications. Theme logic stays in frontend configuration (CSS variables, theme provider, or TailwindCSS config).

### Principle IV: Spec-Driven Development
✅ **PASS** - Feature has complete specification with user stories, acceptance criteria, and success criteria. Following spec → plan → tasks → implement workflow.

### Principle V: Production-Oriented Development
✅ **PASS** - Changes will use proper CSS practices, environment-agnostic configuration, and be tested across browsers. Theme switching will be performant and responsive design will be maintained.

**Initial Constitution Check Result**: ✅ ALL GATES PASSED

---

### Post-Design Re-Evaluation (After Phase 0 & 1)

**Critical Finding from Research**: Dark mode does not currently exist in the application. The feature scope has expanded from "fixing contrast in both modes" to "implementing dark mode + ensuring proper contrast."

### Principle I: Functional Correctness Across All Layers
✅ **PASS** - Research confirms light mode already meets WCAG 2.1 AA standards. Dark mode implementation will follow same standards. Testing strategy documented in quickstart.md ensures correctness.

### Principle II: Security-First Design
✅ **N/A** - No security implications. Theme preference storage in localStorage is non-sensitive data.

### Principle III: Clear Separation of Concerns
✅ **PASS** - Design maintains frontend-only changes. CSS variables for colors, JavaScript for toggle logic, no backend involvement. Research identified need to refactor Button component to use CSS variables (currently uses inline styles), which improves separation.

### Principle IV: Spec-Driven Development
⚠️ **ATTENTION REQUIRED** - Spec assumes dark mode exists, but research shows it doesn't. This is a scope expansion that should be communicated to stakeholders. However, the spec-driven workflow is being followed correctly (spec → plan → research → design).

**Recommendation**: Update spec or get stakeholder approval for expanded scope.

### Principle V: Production-Oriented Development
✅ **PASS** - Design includes proper testing strategy (Lighthouse, axe DevTools, cross-browser), performance considerations (<50ms theme switching), and production-ready implementation approach (CSS variables, localStorage persistence).

**Post-Design Constitution Check Result**: ✅ ALL GATES PASSED (with scope clarification needed)

## Project Structure

### Documentation (this feature)

```text
specs/001-theme-contrast-fix/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── checklists/
│   └── requirements.md  # Spec quality checklist (already created)
└── spec.md              # Feature specification (already created)
```

Note: `data-model.md` and `contracts/` are not applicable for this frontend-only styling feature.

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components (buttons, links, headings, etc.)
│   ├── styles/           # Global styles and theme configuration
│   │   ├── globals.css   # Global CSS with theme variables
│   │   └── theme.ts      # Theme configuration (if using theme provider)
│   └── lib/              # Utility functions
└── tests/
    └── accessibility/    # Accessibility tests for contrast validation
```

**Structure Decision**: This is a web application with separate frontend and backend. The theme contrast fix only affects the `frontend/` directory. All changes will be in styling files (CSS, theme configuration) and potentially component files if inline styles need adjustment. No backend or database changes required.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitution violations. All gates passed.

## Phase 0: Research & Discovery

### Research Tasks

1. **Current Theme Implementation Discovery**
   - **Goal**: Understand how the current theme system is implemented
   - **Questions to Answer**:
     - Where are theme colors defined? (CSS variables, theme provider, TailwindCSS config)
     - How is dark/light mode switching implemented?
     - What components use theme colors?
     - Are there any existing color constants or design tokens?
   - **Method**: Explore `frontend/src/styles/`, `frontend/src/app/`, component files
   - **Output**: Document current theme architecture in research.md

2. **Color Inventory & Contrast Audit**
   - **Goal**: Identify all text colors and their contrast ratios
   - **Questions to Answer**:
     - What colors are currently used for headings, paragraphs, buttons, links?
     - What are the current contrast ratios in light and dark modes?
     - Which elements fail WCAG 2.1 Level AA standards?
   - **Method**: Extract colors from CSS/theme files, calculate contrast ratios
   - **Output**: Table of current colors with contrast ratios and pass/fail status

3. **WCAG 2.1 Contrast Standards Research**
   - **Goal**: Understand exact requirements and calculation methods
   - **Questions to Answer**:
     - How to calculate contrast ratios?
     - What are the exact thresholds for Level AA?
     - What tools can automate contrast checking?
   - **Method**: Review WCAG 2.1 documentation, research contrast calculation formulas
   - **Output**: Document standards and recommended tools

4. **Accessibility Testing Tools Evaluation**
   - **Goal**: Identify tools for automated contrast validation
   - **Questions to Answer**:
     - What tools can check contrast ratios? (axe-core, Lighthouse, WAVE)
     - Can these be integrated into the development workflow?
     - How to test across different browsers?
   - **Method**: Research and evaluate accessibility testing tools
   - **Output**: Recommended tools and integration approach

5. **Browser Compatibility Research**
   - **Goal**: Ensure theme changes work consistently across browsers
   - **Questions to Answer**:
     - Are there any browser-specific CSS color rendering issues?
     - How to test across Chrome, Firefox, Safari, Edge?
     - What color formats are most compatible? (hex, rgb, hsl)
   - **Method**: Research CSS color compatibility and browser testing approaches
   - **Output**: Browser testing strategy and color format recommendations

### Research Output Structure

Create `research.md` with the following sections:

```markdown
# Research: Frontend Theme Contrast Fix

## Current Theme Architecture
[Document findings from Task 1]

## Color Inventory & Contrast Audit
[Table from Task 2 with current colors and contrast ratios]

## WCAG 2.1 Standards
[Standards and calculation methods from Task 3]

## Accessibility Testing Tools
[Recommended tools from Task 4]

## Browser Compatibility Strategy
[Testing approach from Task 5]

## Decisions & Rationale
[Key decisions made based on research]
```

## Phase 1: Design & Implementation Strategy

### Design Artifacts

Since this is a frontend styling feature with no data entities or API contracts, Phase 1 will produce:

1. **quickstart.md** - Testing and validation guide
   - How to run the frontend application
   - How to switch between light and dark modes
   - How to test contrast ratios using accessibility tools
   - How to verify changes across browsers
   - Manual testing checklist

2. **Color Palette Design** (in research.md or separate file)
   - Proposed color values for light mode
   - Proposed color values for dark mode
   - Contrast ratio calculations for each color pair
   - Justification for color choices

### Implementation Strategy

**Approach**: Centralized theme configuration with CSS variables or theme provider

**Steps**:
1. Define new color palette that meets WCAG 2.1 AA standards
2. Update theme configuration (CSS variables, theme provider, or TailwindCSS config)
3. Apply new colors to all text elements (headings, paragraphs, buttons, links)
4. Test across all pages and components
5. Validate with accessibility tools
6. Verify browser compatibility

**Testing Strategy**:
- Automated: Run Lighthouse accessibility audits, axe-core tests
- Manual: Visual inspection of all pages in both modes
- Cross-browser: Test on Chrome, Firefox, Safari, Edge
- Zoom levels: Test at 100%, 150%, 200% zoom

### Agent Context Update

After completing Phase 1 design, run:

```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This will update the Claude-specific context file with:
- Theme contrast fix feature added to active technologies
- WCAG 2.1 Level AA compliance requirement
- Accessibility testing tools in use

## Phase 2: Task Breakdown

**Note**: Phase 2 (task generation) is handled by the `/sp.tasks` command, not `/sp.plan`. This plan provides the foundation for task generation.

### Expected Task Categories

1. **Setup & Discovery Tasks**
   - Explore current theme implementation
   - Audit current colors and contrast ratios
   - Set up accessibility testing tools

2. **Design Tasks**
   - Design new color palette for light mode
   - Design new color palette for dark mode
   - Calculate and verify contrast ratios

3. **Implementation Tasks**
   - Update theme configuration with new colors
   - Apply colors to headings (H1-H6)
   - Apply colors to paragraphs and body text
   - Apply colors to buttons
   - Apply colors to links
   - Test theme switching functionality

4. **Testing & Validation Tasks**
   - Run automated accessibility audits
   - Manual visual testing in light mode
   - Manual visual testing in dark mode
   - Cross-browser testing
   - Zoom level testing

5. **Documentation Tasks**
   - Document color palette decisions
   - Update component documentation if needed

## Risk Mitigation Strategies

### Risk 1: Breaking Visual Consistency
**Mitigation**:
- Preserve brand identity by adjusting colors minimally
- Use color relationships (hue, saturation) to maintain visual harmony
- Get design review before finalizing colors
- Consider A/B testing if significant changes needed

### Risk 2: Incomplete Coverage
**Mitigation**:
- Create comprehensive component inventory before starting
- Use automated tools to scan all pages
- Manual checklist for each component type
- Regression testing after changes

### Risk 3: Browser Compatibility Issues
**Mitigation**:
- Use standardized CSS color formats (hex or rgb)
- Test on all major browsers early
- Use CSS variables for consistency
- Avoid browser-specific CSS features

## Success Metrics

### Acceptance Criteria (from spec)
- All text elements meet WCAG 2.1 Level AA contrast ratios
- Light mode: All text clearly readable
- Dark mode: All text clearly readable
- Interactive elements visually distinguishable
- Theme switching works instantly
- No visual regressions

### Validation Methods
- Automated: Lighthouse accessibility score 100 for contrast
- Automated: axe-core reports zero contrast violations
- Manual: Visual inspection checklist completed
- Manual: Cross-browser testing completed
- Manual: Zoom level testing completed

## Next Steps

1. **Execute Phase 0**: Run research tasks to understand current implementation
2. **Create research.md**: Document all findings and decisions
3. **Execute Phase 1**: Design new color palette and create quickstart.md
4. **Update agent context**: Run update script to add feature to context
5. **Run `/sp.tasks`**: Generate detailed task breakdown for implementation
6. **Execute tasks**: Implement changes following task order
7. **Validate**: Run all tests and verify acceptance criteria

## Notes

- This is a frontend-only feature with no backend or database changes
- No new data entities or API contracts needed
- Focus is on CSS/styling changes to meet accessibility standards
- Changes should be minimal and preserve visual aesthetics
- All changes must be testable and verifiable

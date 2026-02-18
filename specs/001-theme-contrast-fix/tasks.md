# Tasks: Frontend Theme Contrast Fix

**Input**: Design documents from `/specs/001-theme-contrast-fix/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: No test tasks included (not requested in specification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for source code
- All paths relative to repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install accessibility testing tools and prepare development environment

- [x] T001 Install Lighthouse CLI for automated accessibility audits: `npm install -g lighthouse`
- [x] T002 [P] Install axe-core for accessibility testing: `cd frontend && npm install --save-dev @axe-core/react`
- [x] T003 [P] Create accessibility testing directory structure: `frontend/tests/accessibility/`
- [x] T004 Document current theme architecture findings from research.md in frontend/README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Audit current colors, design dark mode palette, and prepare CSS structure

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Audit all current colors in frontend/src/app/globals.css and document in specs/001-theme-contrast-fix/color-audit.md
- [x] T006 Calculate contrast ratios for all current light mode colors using WebAIM Contrast Checker
- [x] T007 Design dark mode color palette with WCAG 2.1 AA compliant contrast ratios (4.5:1 minimum)
- [x] T008 Document final dark mode color palette in specs/001-theme-contrast-fix/dark-mode-palette.md
- [x] T009 Add dark mode CSS variables to frontend/src/app/globals.css under `.dark` selector
- [x] T010 Verify CSS variable structure supports both light and dark modes

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Reading Content in Light Mode (Priority: P1) 🎯 MVP

**Goal**: Verify and ensure all text content in light mode meets WCAG 2.1 Level AA contrast standards

**Independent Test**: View all pages in light mode and verify all text elements (headings, paragraphs, labels) are clearly readable without zooming. Run Lighthouse accessibility audit and confirm zero contrast violations.

### Implementation for User Story 1

- [x] T011 [P] [US1] Verify heading contrast (H1-H6) in frontend/src/app/globals.css meets 4.5:1 ratio
- [x] T012 [P] [US1] Verify paragraph text contrast in frontend/src/app/globals.css meets 4.5:1 ratio
- [x] T013 [P] [US1] Verify muted text contrast in frontend/src/app/globals.css meets 4.5:1 ratio
- [x] T014 [US1] Run Lighthouse accessibility audit on all pages (/, /login, /register, /dashboard) in light mode
- [x] T015 [US1] Fix any light mode contrast violations found in audit by adjusting colors in frontend/src/app/globals.css
- [x] T016 [US1] Test light mode readability at 100%, 150%, and 200% zoom levels
- [x] T017 [US1] Document light mode contrast validation results in specs/001-theme-contrast-fix/validation-light-mode.md

**Checkpoint**: Light mode should meet all WCAG 2.1 AA standards and be independently testable

---

## Phase 4: User Story 2 - Reading Content in Dark Mode (Priority: P1)

**Goal**: Implement dark mode and ensure all text content meets WCAG 2.1 Level AA contrast standards

**Independent Test**: Switch to dark mode (by manually adding `dark` class to `<html>` element) and verify all text elements are clearly readable without glare. Run Lighthouse accessibility audit in dark mode and confirm zero contrast violations.

### Implementation for User Story 2

- [x] T018 [P] [US2] Apply dark mode background colors to frontend/src/app/globals.css (--bg-site, --card-bg)
- [x] T019 [P] [US2] Apply dark mode text colors to frontend/src/app/globals.css (--text-main, --text-muted)
- [x] T020 [P] [US2] Apply dark mode primary colors to frontend/src/app/globals.css (--primary, --primary-hover)
- [x] T021 [P] [US2] Apply dark mode success color to frontend/src/app/globals.css (--success)
- [x] T022 [US2] Test dark mode by manually adding `dark` class to `<html>` element in frontend/src/app/layout.tsx
- [x] T023 [US2] Verify heading contrast (H1-H6) in dark mode meets 4.5:1 ratio
- [x] T024 [US2] Verify paragraph text contrast in dark mode meets 4.5:1 ratio
- [x] T025 [US2] Run Lighthouse accessibility audit on all pages in dark mode
- [x] T026 [US2] Fix any dark mode contrast violations by adjusting colors in frontend/src/app/globals.css
- [x] T027 [US2] Test dark mode readability at 100%, 150%, and 200% zoom levels
- [x] T028 [US2] Remove manual `dark` class addition from frontend/src/app/layout.tsx (prepare for toggle implementation)
- [x] T029 [US2] Document dark mode contrast validation results in specs/001-theme-contrast-fix/validation-dark-mode.md

**Checkpoint**: Dark mode should be fully functional with proper contrast ratios

---

## Phase 5: User Story 3 - Identifying Interactive Elements (Priority: P2)

**Goal**: Ensure buttons and links are visually distinguishable with proper contrast in both light and dark modes

**Independent Test**: View all pages in both modes and verify buttons and links are clearly identifiable. Test hover and focus states for visibility.

### Implementation for User Story 3

- [ ] T030 [US3] Refactor Button component to use CSS variables instead of inline styles in frontend/src/components/ui/Button.tsx
- [ ] T031 [P] [US3] Define button color CSS variables for light mode in frontend/src/app/globals.css
- [ ] T032 [P] [US3] Define button color CSS variables for dark mode in frontend/src/app/globals.css
- [ ] T033 [US3] Verify primary button contrast in light mode (text on background) meets 4.5:1 ratio
- [ ] T034 [US3] Verify primary button contrast in dark mode (text on background) meets 4.5:1 ratio
- [ ] T035 [US3] Verify secondary button contrast in both modes meets 4.5:1 ratio
- [ ] T036 [US3] Verify danger button contrast in both modes meets 4.5:1 ratio
- [ ] T037 [US3] Verify success button contrast in both modes meets 4.5:1 ratio
- [ ] T038 [US3] Test button hover states for visibility in both modes
- [ ] T039 [US3] Test button focus states for visibility in both modes
- [ ] T040 [P] [US3] Verify link contrast in light mode in frontend/src/app/globals.css
- [ ] T041 [P] [US3] Verify link contrast in dark mode in frontend/src/app/globals.css
- [ ] T042 [US3] Test link hover states for visibility in both modes
- [ ] T043 [US3] Run Lighthouse audit on interactive elements in both modes
- [ ] T044 [US3] Document interactive element contrast validation in specs/001-theme-contrast-fix/validation-interactive.md

**Checkpoint**: All interactive elements should be clearly distinguishable in both modes

---

## Phase 6: User Story 4 - Switching Between Modes (Priority: P3)

**Goal**: Implement theme toggle functionality with localStorage persistence and system preference detection

**Independent Test**: Toggle between light and dark modes multiple times and verify theme switches instantly, preference persists after page reload, and system preference is respected by default.

### Implementation for User Story 4

- [ ] T045 [US4] Create theme utility functions in frontend/src/lib/theme.ts (getSystemTheme, getStoredTheme, setTheme)
- [ ] T046 [US4] Implement theme detection logic that respects system preference by default in frontend/src/lib/theme.ts
- [ ] T047 [US4] Implement localStorage persistence for theme preference in frontend/src/lib/theme.ts
- [ ] T048 [US4] Create ThemeProvider context in frontend/src/lib/theme.tsx
- [ ] T049 [US4] Add ThemeProvider to root layout in frontend/src/app/layout.tsx
- [ ] T050 [US4] Create ThemeToggle component in frontend/src/components/ui/ThemeToggle.tsx
- [ ] T051 [US4] Add ThemeToggle component to dashboard header in frontend/src/app/dashboard/page.tsx
- [ ] T052 [US4] Test theme toggle switches instantly (<50ms) with no visible delay
- [ ] T053 [US4] Test theme preference persists after page reload
- [ ] T054 [US4] Test system preference detection works correctly
- [ ] T055 [US4] Test theme switching on all pages (/, /login, /register, /dashboard)
- [ ] T056 [US4] Verify no layout shifts or flashing during theme switch
- [ ] T057 [US4] Document theme toggle implementation in specs/001-theme-contrast-fix/theme-toggle-guide.md

**Checkpoint**: Theme switching should work seamlessly with proper persistence

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cross-browser testing, and documentation

- [ ] T058 [P] Run Lighthouse accessibility audit on all pages in both modes and verify 100 score for contrast
- [ ] T059 [P] Run axe DevTools on all pages in both modes and verify zero contrast violations
- [ ] T060 [P] Test application in Chrome browser (light and dark modes)
- [ ] T061 [P] Test application in Firefox browser (light and dark modes)
- [ ] T062 [P] Test application in Safari browser if available (light and dark modes)
- [ ] T063 [P] Test application in Edge browser (light and dark modes)
- [ ] T064 Test application on mobile Chrome (Android) in both modes
- [ ] T065 Test application on mobile Safari (iOS) in both modes
- [ ] T066 Verify all edge cases from spec.md (zoom levels, browser extensions, OS high contrast mode)
- [ ] T067 Run complete validation checklist from specs/001-theme-contrast-fix/quickstart.md
- [ ] T068 Update frontend/README.md with theme usage instructions
- [ ] T069 Create before/after screenshots for documentation in specs/001-theme-contrast-fix/screenshots/
- [ ] T070 Final code cleanup and remove any debug code or comments

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion
- **User Story 3 (Phase 5)**: Depends on US1 and US2 completion (needs both modes working)
- **User Story 4 (Phase 6)**: Depends on US2 completion (needs dark mode to exist)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories (can run parallel with US1)
- **User Story 3 (P2)**: Depends on US1 and US2 completion - Needs both modes working to test interactive elements
- **User Story 4 (P3)**: Depends on US2 completion - Cannot toggle to dark mode if it doesn't exist

### Within Each User Story

- **US1**: All verification tasks can run in parallel (marked [P])
- **US2**: Color application tasks can run in parallel (T018-T021), then verification tasks sequentially
- **US3**: Button and link tasks can run in parallel where marked [P]
- **US4**: Sequential implementation (utility → provider → component → integration)

### Parallel Opportunities

- **Phase 1**: T002 and T003 can run in parallel
- **Phase 3 (US1)**: T011, T012, T013 can run in parallel (different verification tasks)
- **Phase 4 (US2)**: T018, T019, T020, T021 can run in parallel (applying different color variables)
- **Phase 5 (US3)**: T031 and T032 can run in parallel, T040 and T041 can run in parallel
- **Phase 7**: T058-T063 can run in parallel (different browsers/tools)

---

## Parallel Example: User Story 2 (Dark Mode Implementation)

```bash
# Launch all color application tasks together:
Task: "Apply dark mode background colors to frontend/src/app/globals.css"
Task: "Apply dark mode text colors to frontend/src/app/globals.css"
Task: "Apply dark mode primary colors to frontend/src/app/globals.css"
Task: "Apply dark mode success color to frontend/src/app/globals.css"

# Then verify sequentially after all colors applied
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Light Mode Verification)
4. **STOP and VALIDATE**: Test light mode independently using quickstart.md
5. Deploy/demo if ready (light mode only)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Light mode validated)
3. Add User Story 2 → Test independently → Deploy/Demo (Dark mode working, manual toggle)
4. Add User Story 3 → Test independently → Deploy/Demo (Interactive elements polished)
5. Add User Story 4 → Test independently → Deploy/Demo (Full theme toggle functionality)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (light mode verification)
   - Developer B: User Story 2 (dark mode implementation)
3. After US1 and US2 complete:
   - Developer A: User Story 3 (interactive elements)
   - Developer B: User Story 4 (theme toggle)
4. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 70
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (US1 - Light Mode): 7 tasks
- Phase 4 (US2 - Dark Mode): 12 tasks
- Phase 5 (US3 - Interactive Elements): 15 tasks
- Phase 6 (US4 - Theme Toggle): 13 tasks
- Phase 7 (Polish): 13 tasks

**Parallel Opportunities**: 18 tasks marked [P] can run in parallel within their phases

**Independent Test Criteria**:
- US1: View all pages in light mode, run Lighthouse, verify readability
- US2: Manually add dark class, view all pages, run Lighthouse, verify readability
- US3: Test buttons and links in both modes, verify hover/focus states
- US4: Toggle theme multiple times, verify persistence and system preference

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1 only) = Light mode validation

---

## Notes

- [P] tasks = different files or independent operations, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No tests included (not requested in specification)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Research found dark mode doesn't exist yet - US2 implements it from scratch
- Light mode already meets WCAG 2.1 AA standards per research findings

# Tasks: Authorization & User Isolation Layer

**Input**: Design documents from `/specs/003-auth-isolation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Security testing is a core requirement for this feature and is included throughout.

**Organization**: Tasks are grouped by user story to enable independent validation and testing of each security requirement.

**Key Context**: The authorization layer is already substantially implemented in 002-backend-api-db. This feature focuses on validation, strengthening gaps, comprehensive security testing, and documentation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- All tasks affect backend only (no frontend changes)

---

## Phase 1: Setup (Documentation Infrastructure)

**Purpose**: Initialize documentation and testing infrastructure for authorization validation

- [x] T001 Create security test directory structure (backend/tests/security/)
- [x] T002 [P] Create test fixtures for multi-user scenarios in backend/tests/conftest.py
- [x] T003 [P] Document authorization architecture in specs/003-auth-isolation/architecture.md

**Checkpoint**: Testing infrastructure ready for security validation

---

## Phase 2: Foundational (Code Review & Baseline)

**Purpose**: Review existing authorization implementation and establish baseline

**⚠️ CRITICAL**: Complete review before strengthening or testing

- [x] T004 Review existing JWT validation in backend/src/utils/jwt.py (get_current_user, decode_token)
- [x] T005 Review existing ownership verification in backend/src/api/tasks.py (all 5 endpoints)
- [x] T006 Review existing query filtering in backend/src/api/tasks.py (GET /tasks endpoint)
- [x] T007 Review existing error handling for 401/403 responses across all endpoints
- [x] T008 Document findings in specs/003-auth-isolation/review-findings.md

**Checkpoint**: Baseline established - gaps identified for strengthening

---

## Phase 3: User Story 1 - Task Ownership Enforcement (Priority: P1) 🎯 MVP

**Goal**: Validate and strengthen ownership verification on all task operations to prevent horizontal privilege escalation

**Independent Test**: Create two users (Alice and Bob). Alice creates a task. Bob attempts to access, modify, or delete Alice's task. All operations must fail with 403 Forbidden.

### Implementation for User Story 1

- [x] T009 [P] [US1] Strengthen ownership verification in GET /tasks/{id} endpoint (backend/src/api/tasks.py)
- [x] T010 [P] [US1] Strengthen ownership verification in PUT /tasks/{id} endpoint (backend/src/api/tasks.py)
- [x] T011 [P] [US1] Strengthen ownership verification in DELETE /tasks/{id} endpoint (backend/src/api/tasks.py)
- [x] T012 [US1] Add authorization failure logging to all ownership checks (backend/src/api/tasks.py)
- [x] T013 [US1] Verify GET /tasks query filtering by user_id (backend/src/api/tasks.py)
- [x] T014 [US1] Verify POST /tasks ignores user_id from request body (backend/src/api/tasks.py)

### Security Tests for User Story 1

- [x] T015 [P] [US1] Create test for cross-user GET attempt (backend/tests/security/test_ownership.py)
- [x] T016 [P] [US1] Create test for cross-user UPDATE attempt (backend/tests/security/test_ownership.py)
- [x] T017 [P] [US1] Create test for cross-user DELETE attempt (backend/tests/security/test_ownership.py)
- [x] T018 [P] [US1] Create test for task list isolation (backend/tests/security/test_ownership.py)
- [x] T019 [US1] Create test for parameter manipulation prevention (backend/tests/security/test_ownership.py)

**Checkpoint**: Ownership enforcement validated - users can only access their own tasks

---

## Phase 4: User Story 2 - Token Integrity Validation (Priority: P1) 🎯 MVP

**Goal**: Validate and strengthen JWT token validation to prevent token tampering and replay attacks

**Independent Test**: Attempt to access protected endpoints with: (1) no token, (2) expired token, (3) tampered token, (4) invalid signature. All must fail with 401 Unauthorized.

### Implementation for User Story 2

- [x] T020 [P] [US2] Strengthen JWT signature verification in backend/src/utils/jwt.py (decode_token function)
- [x] T021 [P] [US2] Strengthen token expiration check in backend/src/utils/jwt.py (decode_token function)
- [x] T022 [US2] Add detailed error messages for token validation failures (backend/src/utils/jwt.py)
- [x] T023 [US2] Add token validation failure logging (backend/src/utils/jwt.py)
- [x] T024 [US2] Verify get_current_user dependency extracts user correctly (backend/src/utils/jwt.py)

### Security Tests for User Story 2

- [x] T025 [P] [US2] Create test for missing authentication header (backend/tests/security/test_token_validation.py)
- [x] T026 [P] [US2] Create test for expired token rejection (backend/tests/security/test_token_validation.py)
- [x] T027 [P] [US2] Create test for tampered token rejection (backend/tests/security/test_token_validation.py)
- [x] T028 [P] [US2] Create test for invalid signature rejection (backend/tests/security/test_token_validation.py)
- [x] T029 [US2] Create test for valid token acceptance (backend/tests/security/test_token_validation.py)

**Checkpoint**: Token validation hardened - all tampering attempts are blocked

---

## Phase 5: User Story 3 - Centralized Authorization Logic (Priority: P2)

**Goal**: Validate that authorization logic is centralized and consistently applied across all endpoints

**Independent Test**: Review codebase to confirm authorization logic exists in a single location and all endpoints use the same dependency injection pattern.

### Implementation for User Story 3

- [x] T030 [US3] Audit all task endpoints for consistent use of get_current_user dependency (backend/src/api/tasks.py)
- [x] T031 [US3] Verify no authorization logic duplication across endpoints (backend/src/api/)
- [x] T032 [US3] Document authorization dependency pattern in specs/003-auth-isolation/patterns.md
- [x] T033 [US3] Create example of adding new protected endpoint (specs/003-auth-isolation/examples/new-endpoint.py)
- [x] T034 [US3] Verify fail-secure behavior (missing dependency causes type error)

**Checkpoint**: Authorization is centralized - new endpoints automatically inherit protection

---

## Phase 6: User Story 4 - Security Audit and Penetration Testing (Priority: P2)

**Goal**: Validate system withstands common authorization attacks through comprehensive security testing

**Independent Test**: Run complete security test suite covering all attack vectors. All attacks must be blocked.

### Security Tests for User Story 4

- [x] T035 [P] [US4] Create IDOR (Insecure Direct Object Reference) attack test (backend/tests/security/test_attacks.py)
- [x] T036 [P] [US4] Create horizontal privilege escalation test (backend/tests/security/test_attacks.py)
- [x] T037 [P] [US4] Create token replay attack test (backend/tests/security/test_attacks.py)
- [x] T038 [P] [US4] Create concurrent request race condition test (backend/tests/security/test_attacks.py)
- [x] T039 [US4] Create parameter manipulation attack test (backend/tests/security/test_attacks.py)

### Implementation for User Story 4

- [x] T040 [US4] Run manual security test suite from quickstart.md (all 6 test scenarios)
- [x] T041 [US4] Document security test results in specs/003-auth-isolation/test-results.md
- [x] T042 [US4] Fix any vulnerabilities discovered during testing
- [x] T043 [US4] Re-run security tests to verify fixes

**Checkpoint**: System passes all security tests - no critical vulnerabilities

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and production readiness

- [x] T044 [P] Verify authorization logging is comprehensive (backend/src/api/tasks.py, backend/src/utils/jwt.py)
- [x] T045 [P] Verify error responses don't leak sensitive information (backend/src/middleware/error_handler.py)
- [x] T046 [P] Update API documentation with authorization requirements (specs/003-auth-isolation/contracts/authorization.md)
- [x] T047 Measure authorization performance overhead (should be <50ms)
- [x] T048 Create authorization troubleshooting guide (specs/003-auth-isolation/troubleshooting.md)
- [x] T049 Final security checklist validation (all items from quickstart.md)
- [x] T050 Update CLAUDE.md with authorization patterns and best practices

**Checkpoint**: Feature complete - authorization layer production-ready

---

## Dependencies

### User Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) + Phase 4 (US2) → Phase 5 (US3) + Phase 6 (US4) → Phase 7 (Polish)
                                              ↓                                ↓
                                           [Can run in parallel]          [Can run in parallel]
```

**Critical Path**:
1. Phase 1 & 2 must complete first (setup and baseline)
2. US1 and US2 are P1 (MVP) - can run in parallel after Phase 2
3. US3 and US4 are P2 - can run in parallel after US1 and US2
4. Phase 7 (Polish) requires all user stories complete

**MVP Scope**: Phases 1-4 (US1 and US2 complete)
- Task ownership enforcement validated
- Token integrity validation hardened
- Core security requirements met

**Full Feature**: All phases (includes centralization audit and penetration testing)

---

## Parallel Execution Examples

### Phase 3 (US1) - Ownership Enforcement
```bash
# Can run in parallel (different test files):
T015, T016, T017, T018 (all test creation tasks)

# Can run in parallel (different endpoint functions):
T009, T010, T011 (ownership verification strengthening)
```

### Phase 4 (US2) - Token Validation
```bash
# Can run in parallel (different test scenarios):
T025, T026, T027, T028 (all test creation tasks)

# Can run in parallel (different validation aspects):
T020, T021 (signature and expiration checks)
```

### Phase 6 (US4) - Security Testing
```bash
# Can run in parallel (different attack vectors):
T035, T036, T037, T038 (all attack test creation)
```

### Phase 7 (Polish)
```bash
# Can run in parallel (different documentation):
T044, T045, T046 (logging, error handling, API docs)
```

---

## Implementation Strategy

### MVP-First Approach (Phases 1-4)

**Week 1 Focus**: Core Security (US1 + US2)
- Validate ownership enforcement (US1)
- Validate token integrity (US2)
- Run basic security tests
- **Deliverable**: Authorization layer validated and hardened

**Week 2 Focus**: Comprehensive Validation (US3 + US4)
- Audit centralization (US3)
- Run penetration tests (US4)
- **Deliverable**: Full security validation complete

### Incremental Delivery

Each user story delivers independently testable value:
- **After US1**: Ownership enforcement validated
- **After US2**: Token validation hardened
- **After US3**: Centralization confirmed
- **After US4**: Security testing complete

---

## Testing Strategy

### Security Test Coverage

**Unit Tests**: Not applicable (validation-focused feature)

**Integration Tests**: Security tests validate authorization across endpoints
- Cross-user access attempts (US1)
- Token tampering attempts (US2)
- Attack vector resistance (US4)

**Manual Tests**: Comprehensive security test suite in quickstart.md
- 6 test scenarios with cURL commands
- Postman collection for organized testing
- Performance testing for authorization overhead

### Test Execution Order

1. **Phase 3 Tests (US1)**: Ownership enforcement
2. **Phase 4 Tests (US2)**: Token validation
3. **Phase 6 Tests (US4)**: Attack resistance
4. **Phase 7 Tests**: Performance and final validation

---

## Task Summary

**Total Tasks**: 50
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (US1 - P1): 11 tasks (6 implementation + 5 tests)
- Phase 4 (US2 - P1): 10 tasks (5 implementation + 5 tests)
- Phase 5 (US3 - P2): 5 tasks
- Phase 6 (US4 - P2): 9 tasks (5 tests + 4 implementation)
- Phase 7 (Polish): 7 tasks

**Parallel Opportunities**: 20 tasks marked [P] (40% parallelizable)

**MVP Scope**: Phases 1-4 (29 tasks) - Core security validation
**Full Feature**: All phases (50 tasks) - Complete security validation and testing

**Estimated Effort**:
- MVP (Phases 1-4): 2-3 days (validation and basic testing)
- Full Feature (All phases): 4-5 days (includes comprehensive penetration testing)

---

## Success Criteria

✅ **After Phase 3 (US1)**:
- Users can only access their own tasks
- Cross-user access attempts return 403 Forbidden
- Task list shows only user's own tasks

✅ **After Phase 4 (US2)**:
- Tampered tokens are rejected with 401 Unauthorized
- Expired tokens are rejected with 401 Unauthorized
- Valid tokens are accepted and user identity extracted

✅ **After Phase 5 (US3)**:
- Authorization logic is centralized in dependencies
- No code duplication across endpoints
- New endpoints automatically inherit authorization

✅ **After Phase 6 (US4)**:
- System passes all security tests
- No critical or high-severity vulnerabilities
- Attack vectors are blocked

✅ **After Phase 7 (Polish)**:
- Authorization overhead <50ms
- Comprehensive logging in place
- Documentation complete
- Production-ready

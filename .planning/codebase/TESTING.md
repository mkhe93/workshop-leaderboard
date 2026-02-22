# Testing Patterns

**Analysis Date:** 2026-02-22

## Test Framework

**Runner:**
- Frontend: Vitest 4.x
  - Config: `/IdeaProjects/leaderboard/frontend/vitest.config.js`
  - Uses `@vitejs/plugin-vue` and the `jsdom` environment with `globals: true`.
- Backend: pytest 8.x
  - Config: Standard `pytest` discovery with a `conftest.py` module: `/IdeaProjects/leaderboard/backend/tests/conftest.py`.

**Assertion Library:**
- Frontend: Vitest's Jest-compatible assertions (`expect`, `toBe`, `toHaveLength`, etc.) imported from `vitest`.
- Backend: Built-in `assert` statements and `pytest.raises` for exception assertions.

**Run Commands:**
```bash
# Frontend (from /IdeaProjects/leaderboard/frontend)
npm test                 # "vitest src/" - run all unit tests under src
npm run coverage         # "vitest run --coverage" - run tests with coverage

# Backend (from /IdeaProjects/leaderboard/backend)
pytest                   # Discover and run all tests in backend/tests
pytest backend/tests     # Explicit test directory
```

## Test File Organization

**Location:**
- Frontend: Tests are co-located with the components or helpers they test under `frontend/src`, e.g.:
  - `/IdeaProjects/leaderboard/frontend/src/components/features/filters/DateRangeSelector.test.js`
  - `/IdeaProjects/leaderboard/frontend/src/components/features/charts/TokenTypeBreakdown.test.js`
  - `/IdeaProjects/leaderboard/frontend/src/components/SharedControls.test.js`
  - `/IdeaProjects/leaderboard/frontend/src/helpers/helpers.test.js`
  - `/IdeaProjects/leaderboard/frontend/src/views/ChartsView.test.js`
- Backend: Tests live in a dedicated `backend/tests` package:
  - Integration and service tests are grouped by feature: `test_tokens_endpoint_integration.py`, `test_tokens_timeseries_endpoint_integration.py`, `test_cost_efficiency_service.py`, `test_success_rate_service.py`, `test_token_aggregation_service.py`.
  - Utility-level tests: `test_date_utils.py`, `test_date_validation.py`, `test_breakdown_edge_cases.py`.

**Naming:**
- Frontend: Test files end with `.test.js` and mirror the unit under test (e.g. `TokenTypeBreakdown.test.js` for `TokenTypeBreakdown.vue`).
- Backend: Test module names start with `test_` and usually mirror the module or feature (e.g. `test_tokens_endpoint_integration.py` tests `/tokens` endpoint behavior).

**Structure:**
```
backend/tests/
├── conftest.py                   # Shared pytest configuration and path setup
├── test_date_utils.py            # Unit tests for src/utils/date_utils.py
├── test_tokens_endpoint_integration.py
├── test_tokens_timeseries_endpoint_integration.py
├── test_cost_efficiency_service.py
├── test_success_rate_service.py
├── test_token_aggregation_service.py
└── ...                           # Additional service and integration tests

frontend/src/components/features/filters/
├── DateRangeSelector.vue
└── DateRangeSelector.test.js

frontend/src/components/features/charts/
├── TokenTypeBreakdown.vue
└── TokenTypeBreakdown.test.js
```

## Test Structure

**Suite Organization (Frontend):**
```javascript
// /IdeaProjects/leaderboard/frontend/src/components/features/filters/DateRangeSelector.test.js
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import DateRangeSelector from './DateRangeSelector.vue'

describe('DateRangeSelector', () => {
  let mockDate

  beforeEach(() => {
    mockDate = new Date('2024-02-15T12:00:00Z')
    vi.setSystemTime(mockDate)
  })

  it('renders start and end date inputs', () => {
    const wrapper = mount(DateRangeSelector, { /* props */ })
    const inputs = wrapper.findAll('input[type="date"]')
    expect(inputs).toHaveLength(2)
  })

  // Additional it(...) cases for behavior and edge cases
})
```

**Suite Organization (Backend):**
```python
# /IdeaProjects/leaderboard/backend/tests/test_date_utils.py
import pytest
from datetime import datetime, timedelta, timezone
from src.utils.date_utils import parse_date_range, format_date_for_api, format_date_for_api_end

class TestParseDateRange:
    """Tests for parse_date_range function."""

    def test_valid_date_parsing_both_dates(self):
        start_dt, end_dt = parse_date_range("2024-01-15", "2024-01-20")
        assert start_dt.year == 2024
        # further assertions ...

    def test_invalid_start_date_format(self):
        with pytest.raises(ValueError) as exc_info:
            parse_date_range("2024/01/15", "2024-01-20")
        assert "Invalid start_date format" in str(exc_info.value)
```

**Patterns:**
- Frontend:
  - Use `describe` blocks per component or helper, `it`/`test` blocks for individual behaviors.
  - Frequent use of the Vue Test Utils `mount` helper to render components and interact with DOM or props.
  - Arrange/Act/Assert phases are often annotated with comments (`// given`, `// when`, `// then`) as in `frontend/src/helpers/helpers.test.js`.
- Backend:
  - Group related tests in `class Test...:` containers with docstrings describing the purpose.
  - Use `pytest.fixture` for shared setup, especially to configure FastAPI app, test client, and mock dependencies.
  - Prefer explicit test names that describe behavior, such as `test_future_date_returns_400` or `test_empty_data_scenario`.

## Mocking

**Framework:**
- Frontend: Uses Vitest's mocking utilities (`vi.mock`, `vi.fn`, `vi.clearAllMocks`, `vi.setSystemTime`). Components and composables are mocked at the module level.
- Backend: Uses `unittest.mock.Mock` from the standard library combined with pytest fixtures and FastAPI's `dependency_overrides` to inject mocks.

**Patterns (Frontend):**
```javascript
// /IdeaProjects/leaderboard/frontend/src/components/features/charts/TokenTypeBreakdown.test.js
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TokenTypeBreakdown from './TokenTypeBreakdown.vue'

// Mock UI components used by the chart
vi.mock('../../ui/LoadingSpinner.vue', () => ({
  default: {
    name: 'LoadingSpinner',
    template: '<div class="loading-spinner">{{ message }}</div>',
    props: ['message']
  }
}))

vi.mock('../../ui/ErrorMessage.vue', () => ({
  default: {
    name: 'ErrorMessage',
    template: '<div class="error-message">{{ message }}</div>',
    props: ['message', 'showRetry']
  }
}))

describe('TokenTypeBreakdown', () => {
  it('shows error state', () => {
    const wrapper = mount(TokenTypeBreakdown, {
      props: { teams: [], loading: false, error: 'Failed to load data', searchTerm: '' }
    })
    expect(wrapper.find('.error-message').exists()).toBe(true)
  })
})
```

```javascript
// /IdeaProjects/leaderboard/frontend/src/views/ChartsView.test.js
vi.mock('../composables/useTokenData.js', () => ({
  useTokenData: () => ({
    data: ref([...]),
    timeSeriesData: ref([...]),
    loading: ref(false),
    error: ref(''),
    fetchData: vi.fn(),
    retry: vi.fn()
  })
}))

// Chart.js components are mocked via vue-chartjs
vi.mock('vue-chartjs', () => ({
  Bar: { name: 'Bar', template: '<div class="mock-chart"></div>', props: ['data', 'options'] },
  // ... other mock chart components
}))
```

**Patterns (Backend):**
```python
# /IdeaProjects/leaderboard/backend/tests/test_tokens_endpoint_integration.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from datetime import datetime, timedelta, timezone

from src.api.server import create_backend
from src.utils.dependency_config import get_api_client
from src.client.models import TeamResponse

@pytest.fixture
def app():
    return create_backend()

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def mock_api_client():
    mock = Mock()
    mock.fetch_teams.return_value = [
        TeamResponse.model_validate({"team_id": "team1", "team_alias": "Alpha Team"}),
        TeamResponse.model_validate({"team_id": "team2", "team_alias": "Beta Team"}),
    ]
    # configure mock_response.model_dump.return_value ...
    return mock

class TestTokensEndpointIntegration:

    def test_success_with_valid_date_range(self, client, app, mock_api_client):
        app.dependency_overrides[get_api_client] = lambda: mock_api_client
        response = client.get("/tokens?start_date=2024-01-01&end_date=2024-01-31")
        assert response.status_code == 200
        # ... more assertions ...
        app.dependency_overrides.clear()
```

**What to Mock:**
- Frontend:
  - Expensive or complex UI primitives (charts, spinners, error components) are replaced with simple mocked components.
  - Composables that fetch remote data are mocked to return stable `ref` values so that tests are deterministic.
- Backend:
  - Dependencies that perform network I/O (API clients) are mocked at the dependency injection level (`get_api_client`) to avoid real HTTP calls.
  - Service methods are indirectly exercised via the API, but external systems (LiteLLM) are always represented by mocks with realistic sample data shapes.

**What NOT to Mock:**
- Backend business logic and utilities are generally not mocked; tests call real implementations of services, utility functions, and endpoint wrappers. For example, `backend/tests/test_date_utils.py` exercises the real `parse_date_range` and formatting functions.
- Frontend layout and behavior logic (like computed properties, v-model bindings, and emitted events) are tested on real components, not mocks.

## Fixtures and Factories

**Test Data:**
```python
# /IdeaProjects/leaderboard/backend/tests/test_tokens_endpoint_integration.py
@pytest.fixture
def mock_api_client():
    mock = Mock()
    mock.fetch_teams.return_value = [
        TeamResponse.model_validate({"team_id": "team1", "team_alias": "Alpha Team"}),
        TeamResponse.model_validate({"team_id": "team2", "team_alias": "Beta Team"}),
    ]
    activity_data = {
        "results": [
            {
                "date": "2024-01-15",
                "metrics": {"total_tokens": 3000, "prompt_tokens": 1800, "completion_tokens": 1200},
                "breakdown": {
                    "entities": {"team1": {"metrics": {...}}, "team2": {"metrics": {...}}},
                    "models": {...},
                    "api_keys": {...},
                },
            }
        ]
    }
    mock_response = Mock()
    mock_response.model_dump.return_value = activity_data
    mock.fetch_team_daily_activity.return_value = mock_response
    return mock
```

```javascript
// /IdeaProjects/leaderboard/frontend/src/helpers/helpers.test.js
const input = [
  {name: 'Group 1', tokens: 10},
  {name: 'Group 2', tokens: 5},
  {name: 'Group 3', tokens: 1},
  {name: 'Group 4', tokens: 0}
]
const result = applyMedals(input)
expect(result[0].medal).toBe('🥇')
```

**Location:**
- Backend fixtures are defined directly in test modules or in shared `backend/tests/conftest.py` for cross-test behavior (path setup for importing `src` by altering `sys.path`).
- Frontend test data is typically inlined in individual tests or at the top of the file in local constants.

## Coverage

**Requirements:**
- No explicit minimum coverage thresholds are enforced in configuration files reviewed. However, there are comprehensive tests around key business rules (date handling, API error handling, cost efficiency calculations, and success rate aggregation) and important UI flows.

**View Coverage:**
```bash
# Frontend
npm run coverage     # in /IdeaProjects/leaderboard/frontend, runs Vitest with coverage

# Backend
pytest --cov=src     # (recommended pattern when adding coverage; not pre-configured in pyproject)
```

## Test Types

**Unit Tests:**
- Backend: Functions in `backend/src/utils/date_utils.py` are covered by `backend/tests/test_date_utils.py`, which asserts behavior across a wide range of inputs (valid dates, invalid formats, leap-year edge cases, and default ranges).
- Frontend: Component-specific tests like `frontend/src/components/features/filters/DateRangeSelector.test.js` and helper tests such as `frontend/src/helpers/helpers.test.js` validate individual units in isolation.

**Integration Tests:**
- Backend: Endpoints are tested via FastAPI `TestClient` in files like:
  - `/IdeaProjects/leaderboard/backend/tests/test_tokens_endpoint_integration.py`
  - `/IdeaProjects/leaderboard/backend/tests/test_tokens_timeseries_endpoint_integration.py`
  - `/IdeaProjects/leaderboard/backend/tests/test_cost_efficiency_endpoint_integration.py`
- These tests stand up the real FastAPI app via `create_backend`, override API clients, and validate response schemas, error codes, and side effects like date range defaults.

**E2E Tests:**
- Frontend: `@playwright/test` is configured as a dev dependency in `/IdeaProjects/leaderboard/frontend/package.json`, with npm scripts `e2e` and `e2e:report`. The actual `e2e/` directory contents are not listed here, but the pattern expects Playwright tests under `frontend/e2e` and a `playwright.config.js`.

## Common Patterns

**Async Testing (Frontend):**
```javascript
// Ensuring DOM updates are processed
it('does not display loading or error states when data is present', async () => {
  const wrapper = mount(ChartView)
  await wrapper.vm.$nextTick()

  expect(wrapper.find('.loading').exists()).toBe(false)
  expect(wrapper.find('.error').exists()).toBe(false)
  expect(wrapper.find('.no-data').exists()).toBe(false)
})
```

**Error Testing (Backend):**
```python
# /IdeaProjects/leaderboard/backend/tests/test_tokens_endpoint_integration.py
def test_invalid_date_format_returns_400(self, client):
    invalid_formats = [
        "2024/01/01",
        "01-01-2024",
        "not-a-date",
        "2024-13-01",
        "2024-01-32",
    ]

    for invalid_date in invalid_formats:
        response = client.get(f"/tokens?start_date={invalid_date}")
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "Date must be in YYYY-MM-DD format" in response.json()["detail"]
```

```python
# /IdeaProjects/leaderboard/backend/tests/test_tokens_endpoint_integration.py
def test_unexpected_error_returns_500(self, client, app, mock_api_client):
    mock_api_client.fetch_team_daily_activity.side_effect = ValueError("Unexpected internal error")
    app.dependency_overrides[get_api_client] = lambda: mock_api_client

    response = client.get("/tokens?start_date=2024-01-01&end_date=2024-01-31")

    assert response.status_code == 500
    assert "Unexpected error" in response.json()["detail"]
    app.dependency_overrides.clear()
```

---

*Testing analysis: 2026-02-22*

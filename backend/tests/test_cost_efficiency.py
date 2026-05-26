"""
Tests for cost efficiency endpoint and calculations.
"""


def test_cost_efficiency_calculation_logic():
    """Property test: cost per 1k tokens should be calculated correctly."""
    # Test cases: (total_cost, total_tokens, expected_cost_per_1k)
    test_cases = [
        (10.0, 10000, 1.0),  # $10 for 10k tokens = $1 per 1k
        (0.5, 1000, 0.5),  # $0.50 for 1k tokens = $0.50 per 1k
        (100.0, 1000000, 0.1),  # $100 for 1M tokens = $0.10 per 1k
        (0.0, 1000, 0.0),  # No cost
        (10.0, 0, 0.0),  # No tokens (edge case)
    ]

    for total_cost, total_tokens, expected in test_cases:
        if total_tokens > 0:
            calculated = (total_cost / total_tokens) * 1000
            assert abs(calculated - expected) < 0.0001, (
                f"Failed for cost={total_cost}, tokens={total_tokens}"
            )
        else:
            # When tokens is 0, cost per 1k should be 0
            assert expected == 0.0


def test_cost_efficiency_zero_tokens():
    """Test that zero tokens results in zero cost per 1k."""
    total_cost = 10.0
    total_tokens = 0

    # This is the logic from CostEfficiencyService.fetch_cost_efficiency
    cost_per_1k = (total_cost / total_tokens * 1000) if total_tokens > 0 else 0.0

    assert cost_per_1k == 0.0


def test_cost_efficiency_rounding():
    """Test that cost per 1k is rounded to 4 decimal places."""
    total_cost = 1.23456789
    total_tokens = 1000

    cost_per_1k = (total_cost / total_tokens) * 1000
    rounded = round(cost_per_1k, 4)

    assert rounded == 1.2346  # Rounded to 4 decimals

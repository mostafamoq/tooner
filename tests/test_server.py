"""Tests for Tooner MCP server tools."""

from src.tooner.server import (
    json_to_toon,
    toon_to_json,
    is_uniform_array,
    estimate_tokens,
    compress_to_toon,
    parse_from_toon,
    compare_token_usage,
    should_use_toon,
)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_estimate_tokens(self):
        """Test token estimation."""
        assert estimate_tokens("hello") > 0
        assert estimate_tokens("a" * 100) > estimate_tokens("a" * 50)

    def test_is_uniform_array_valid(self):
        """Test uniform array detection with valid data."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        assert is_uniform_array(data) is True

    def test_is_uniform_array_invalid(self):
        """Test uniform array detection with invalid data."""
        # Non-uniform keys
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "email": "bob@example.com"},
        ]
        assert is_uniform_array(data) is False

        # Not a list
        assert is_uniform_array({"id": 1}) is False

        # Empty list
        assert is_uniform_array([]) is False

        # List of non-dicts
        assert is_uniform_array([1, 2, 3]) is False


class TestToonConversion:
    """Test Toon format conversion."""

    def test_json_to_toon_uniform_array(self):
        """Test JSON to Toon conversion with uniform array."""
        data = [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
        ]
        result = json_to_toon(data, name="users")

        assert "users[2]{id,name,role}:" in result
        assert "1,Alice,admin" in result
        assert "2,Bob,user" in result

    def test_json_to_toon_single_dict(self):
        """Test JSON to Toon conversion with single dict."""
        data = {"id": 1, "name": "Alice"}
        result = json_to_toon(data, name="user")

        assert "user[1]{id,name}:" in result
        assert "1,Alice" in result

    def test_toon_to_json_uniform_array(self):
        """Test Toon to JSON conversion."""
        toon_str = """users[2]{id,name,role}:
 1,Alice,admin
 2,Bob,user"""

        result = toon_to_json(toon_str)

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Alice"
        assert result[0]["role"] == "admin"
        assert result[1]["id"] == 2
        assert result[1]["name"] == "Bob"

    def test_json_to_toon_with_commas(self):
        """Test handling of values with commas."""
        data = [
            {"id": 1, "name": "Alice, Smith"},
            {"id": 2, "name": "Bob"},
        ]
        result = json_to_toon(data, name="users")

        # Should handle comma in name
        assert "users[2]{id,name}:" in result


class TestMCPTools:
    """Test MCP tool functions."""

    def test_compress_to_toon(self):
        """Test compress_to_toon tool."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        result = compress_to_toon(data, name="users")

        assert "toon" in result
        assert "original_tokens" in result
        assert "toon_tokens" in result
        assert "savings_percent" in result
        assert result["is_uniform"] is True
        assert result["toon_tokens"] < result["original_tokens"]

    def test_parse_from_toon(self):
        """Test parse_from_toon tool."""
        toon_str = """users[2]{id,name}:
 1,Alice
 2,Bob"""

        result = parse_from_toon(toon_str)

        assert result["success"] is True
        assert len(result["json"]) == 2
        assert result["json"][0]["name"] == "Alice"

    def test_compare_token_usage(self):
        """Test compare_token_usage tool."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        result = compare_token_usage(data, name="users")

        assert "json_format" in result
        assert "toon_format" in result
        assert "json_tokens" in result
        assert "toon_tokens" in result
        assert "savings_percent" in result
        assert "recommendation" in result

    def test_should_use_toon_uniform(self):
        """Test should_use_toon with uniform data."""
        data = [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
        ]
        result = should_use_toon(data)

        assert result["is_uniform"] is True
        assert "estimated_savings_percent" in result
        assert "reason" in result
        assert result["array_size"] == 2

    def test_should_use_toon_non_uniform(self):
        """Test should_use_toon with non-uniform data."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "email": "bob@example.com"},
        ]
        result = should_use_toon(data)

        assert result["should_use"] is False
        assert result["is_uniform"] is False
        assert "inconsistent fields" in result["reason"].lower()

    def test_should_use_toon_not_array(self):
        """Test should_use_toon with non-array data."""
        data = {"id": 1, "name": "Alice"}
        result = should_use_toon(data)

        assert result["should_use"] is False
        assert "not an array" in result["reason"].lower()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_data(self):
        """Test handling of empty data."""
        result = should_use_toon([])
        assert result["should_use"] is False
        assert "empty" in result["reason"].lower()

    def test_large_dataset(self):
        """Test with larger dataset to verify token savings."""
        data = [{"id": i, "name": f"User{i}", "role": "user"} for i in range(100)]
        result = compress_to_toon(data)

        # Should see significant savings with large uniform dataset
        assert result["savings_percent"] > 20
        assert result["is_uniform"] is True

    def test_nested_structures(self):
        """Test with nested structures (not ideal for Toon)."""
        data = [
            {"id": 1, "details": {"age": 30, "city": "NYC"}},
            {"id": 2, "details": {"age": 25, "city": "LA"}},
        ]

        # Should still process but may not be as efficient
        result = compress_to_toon(data)
        assert "toon" in result

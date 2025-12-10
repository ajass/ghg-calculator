"""Tests for plugin system."""

import pytest

from ghg_emissions.plugins import (
    CalculatorPlugin,
    FactorProvider,
    PluginManager,
)
from ghg_emissions.models import EmissionFactor, GasType


class MockFactorProvider(FactorProvider):
    """Mock factor provider for testing."""

    @property
    def name(self):
        return "mock_provider"

    @property
    def version(self):
        return "1.0.0"

    def get_factors(self, category=None):
        factors = [
            EmissionFactor(
                gas=GasType.CO2,
                value=0.5,
                unit="kg CO2 per unit",
                source="Mock",
                category="Test"
            )
        ]
        if category:
            return [f for f in factors if f.category == category]
        return factors

    def get_categories(self):
        return ["Test"]


class MockCalculatorPlugin(CalculatorPlugin):
    """Mock calculator plugin for testing."""

    @property
    def name(self):
        return "mock_calculator"

    @property
    def version(self):
        return "1.0.0"

    def calculate_custom(self, activity_data, parameters=None):
        return {"result": "mock calculation"}


class TestPluginManager:
    """Test PluginManager class."""

    @pytest.fixture
    def manager(self):
        """Create plugin manager instance."""
        return PluginManager()

    @pytest.fixture
    def mock_provider(self):
        """Create mock factor provider."""
        return MockFactorProvider()

    @pytest.fixture
    def mock_plugin(self):
        """Create mock calculator plugin."""
        return MockCalculatorPlugin()

    def test_register_factor_provider(self, manager, mock_provider):
        """Test registering a factor provider."""
        manager.register_factor_provider(mock_provider)

        assert "mock_provider" in manager.list_factor_providers()
        assert len(manager.get_all_factors()) == 1

    def test_register_calculator_plugin(self, manager, mock_plugin):
        """Test registering a calculator plugin."""
        manager.register_calculator_plugin(mock_plugin)

        assert "mock_calculator" in manager.list_calculator_plugins()
        plugin = manager.get_calculator_plugin("mock_calculator")
        assert plugin is not None
        assert plugin.name == "mock_calculator"

    def test_get_factors_by_provider(self, manager, mock_provider):
        """Test getting factors from specific provider."""
        manager.register_factor_provider(mock_provider)

        factors = manager.get_factors_by_provider("mock_provider")
        assert len(factors) == 1
        assert factors[0].gas == GasType.CO2

    def test_get_all_factors(self, manager, mock_provider):
        """Test getting all factors from registered providers."""
        manager.register_factor_provider(mock_provider)

        all_factors = manager.get_all_factors()
        assert len(all_factors) == 1

    def test_get_available_categories(self, manager, mock_provider):
        """Test getting available categories."""
        manager.register_factor_provider(mock_provider)

        categories = manager.get_available_categories()
        assert "Test" in categories

    def test_get_factors_by_category(self, manager, mock_provider):
        """Test filtering factors by category."""
        manager.register_factor_provider(mock_provider)

        factors = manager.get_all_factors(category="Test")
        assert len(factors) == 1

        # Test non-existent category
        factors = manager.get_all_factors(category="NonExistent")
        assert len(factors) == 0
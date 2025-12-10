"""Tests for emission calculator."""

import pytest
from datetime import datetime

from ghg_emissions.calculator import EmissionCalculator
from ghg_emissions.models import (
    ActivityData,
    EmissionFactor,
    GasType,
    Scope,
    Unit,
)


class TestEmissionCalculator:
    """Test EmissionCalculator class."""

    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return EmissionCalculator()

    @pytest.fixture
    def sample_factor(self):
        """Create sample emission factor."""
        return EmissionFactor(
            gas=GasType.CO2,
            value=0.5,  # 0.5 kg CO2 per kWh
            unit="kg CO2 per kWh",
            source="Test Source",
            category="Electricity"
        )

    @pytest.fixture
    def sample_activity(self):
        """Create sample activity data."""
        return ActivityData(
            activity_type="Electricity Usage",
            quantity=1000.0,  # 1000 kWh
            unit=Unit.KWH
        )

    def test_calculate_emissions_basic(self, calculator, sample_factor, sample_activity):
        """Test basic emission calculation."""
        record = calculator.calculate_emissions(
            activity=sample_activity,
            factors=[sample_factor],
            scope=Scope.SCOPE_2
        )

        assert record.total_co2e == 500.0  # 1000 * 0.5
        assert len(record.results) == 1
        assert record.results[0].gas == GasType.CO2
        assert record.results[0].amount == 500.0
        assert record.scope == Scope.SCOPE_2

    def test_calculate_emissions_multiple_gases(self, calculator, sample_activity):
        """Test calculation with multiple gas types."""
        factors = [
            EmissionFactor(
                gas=GasType.CO2,
                value=0.4,
                unit="kg CO2 per kWh",
                source="Test",
                category="Electricity"
            ),
            EmissionFactor(
                gas=GasType.CH4,
                value=0.001,
                unit="kg CH4 per kWh",
                source="Test",
                category="Electricity"
            )
        ]

        record = calculator.calculate_emissions(
            activity=sample_activity,
            factors=factors,
            scope=Scope.SCOPE_1
        )

        # CO2: 1000 * 0.4 = 400 kg CO2 = 400 kg CO2e
        # CH4: 1000 * 0.001 = 1 kg CH4 = 1 * 25 = 25 kg CO2e
        # Total: 425 kg CO2e
        assert record.total_co2e == 425.0
        assert len(record.results) == 2

    def test_calculate_emissions_no_factors_raises_error(self, calculator, sample_activity):
        """Test that calculation without factors raises error."""
        with pytest.raises(ValueError, match="At least one emission factor must be provided"):
            calculator.calculate_emissions(
                activity=sample_activity,
                factors=[],
                scope=Scope.SCOPE_1
            )

    def test_calculate_multiple_activities(self, calculator):
        """Test calculating emissions for multiple activities."""
        factors = [
            EmissionFactor(
                gas=GasType.CO2,
                value=0.5,
                unit="kg CO2 per kWh",
                source="Test",
                category="Electricity"
            )
        ]

        activities = [
            ActivityData(activity_type="Electricity", quantity=100.0, unit=Unit.KWH),
            ActivityData(activity_type="Electricity", quantity=200.0, unit=Unit.KWH),
        ]

        records = calculator.calculate_multiple_activities(
            activities=activities,
            factors=factors,
            scope=Scope.SCOPE_2
        )

        assert len(records) == 2
        assert records[0].total_co2e == 50.0  # 100 * 0.5
        assert records[1].total_co2e == 100.0  # 200 * 0.5

    def test_gwp_factors(self, calculator):
        """Test GWP factor access and updates."""
        assert calculator.gwp_factors[GasType.CO2] == 1.0
        assert calculator.gwp_factors[GasType.CH4] == 25.0
        assert calculator.gwp_factors[GasType.N2O] == 298.0

        # Update GWP factors
        calculator.update_gwp_factors({GasType.CH4: 30.0})
        assert calculator.gwp_factors[GasType.CH4] == 30.0

    def test_supported_gases(self, calculator):
        """Test getting supported gases."""
        gases = calculator.get_supported_gases()
        assert GasType.CO2 in gases
        assert GasType.CH4 in gases
        assert GasType.N2O in gases
"""Tests for core data models."""

import pytest
from datetime import datetime

from ghg_emissions.models import (
    ActivityData,
    CalculationRecord,
    EmissionFactor,
    EmissionResult,
    GasType,
    Scope,
    Unit,
)


class TestEmissionFactor:
    """Test EmissionFactor dataclass."""

    def test_valid_emission_factor(self):
        """Test creating a valid emission factor."""
        factor = EmissionFactor(
            gas=GasType.CO2,
            value=0.5,
            unit="kg CO2 per kWh",
            source="Test Source",
            category="Electricity"
        )
        assert factor.gas == GasType.CO2
        assert factor.value == 0.5

    def test_negative_value_raises_error(self):
        """Test that negative values raise ValueError."""
        with pytest.raises(ValueError, match="Emission factor value must be non-negative"):
            EmissionFactor(
                gas=GasType.CO2,
                value=-0.1,
                unit="kg CO2 per kWh",
                source="Test",
                category="Test"
            )


class TestActivityData:
    """Test ActivityData dataclass."""

    def test_valid_activity_data(self):
        """Test creating valid activity data."""
        activity = ActivityData(
            activity_type="Electricity Usage",
            quantity=1000.0,
            unit=Unit.KWH
        )
        assert activity.quantity == 1000.0
        assert activity.unit == Unit.KWH

    def test_negative_quantity_raises_error(self):
        """Test that negative quantities raise ValueError."""
        with pytest.raises(ValueError, match="Activity quantity must be non-negative"):
            ActivityData(
                activity_type="Test",
                quantity=-10.0,
                unit=Unit.KWH
            )


class TestEmissionResult:
    """Test EmissionResult dataclass."""

    def test_valid_emission_result(self):
        """Test creating a valid emission result."""
        factor = EmissionFactor(
            gas=GasType.CO2,
            value=0.5,
            unit="kg CO2 per kWh",
            source="Test",
            category="Electricity"
        )
        activity = ActivityData(
            activity_type="Electricity",
            quantity=100.0,
            unit=Unit.KWH
        )

        result = EmissionResult(
            gas=GasType.CO2,
            amount=50.0,
            unit=Unit.KG,
            co2_equivalent=50.0,
            scope=Scope.SCOPE_2,
            factor_used=factor,
            activity=activity
        )
        assert result.amount == 50.0
        assert result.co2_equivalent == 50.0

    def test_negative_amount_raises_error(self):
        """Test that negative amounts raise ValueError."""
        factor = EmissionFactor(gas=GasType.CO2, value=1.0, unit="test", source="test", category="test")
        activity = ActivityData(activity_type="test", quantity=1.0, unit=Unit.KG)

        with pytest.raises(ValueError, match="Emission amount must be non-negative"):
            EmissionResult(
                gas=GasType.CO2,
                amount=-10.0,
                unit=Unit.KG,
                co2_equivalent=0.0,
                scope=Scope.SCOPE_1,
                factor_used=factor,
                activity=activity
            )


class TestCalculationRecord:
    """Test CalculationRecord dataclass."""

    def test_valid_calculation_record(self):
        """Test creating a valid calculation record."""
        factor = EmissionFactor(gas=GasType.CO2, value=1.0, unit="test", source="test", category="test")
        activity = ActivityData(activity_type="test", quantity=1.0, unit=Unit.KG)
        result = EmissionResult(
            gas=GasType.CO2,
            amount=1.0,
            unit=Unit.KG,
            co2_equivalent=1.0,
            scope=Scope.SCOPE_1,
            factor_used=factor,
            activity=activity
        )

        record = CalculationRecord(
            calculation_id="test-123",
            activity=activity,
            factors_applied=[factor],
            results=[result],
            total_co2e=1.0,
            scope=Scope.SCOPE_1
        )
        assert record.calculation_id == "test-123"
        assert len(record.results) == 1

    def test_empty_results_raises_error(self):
        """Test that empty results raise ValueError."""
        activity = ActivityData(activity_type="test", quantity=1.0, unit=Unit.KG)
        factor = EmissionFactor(gas=GasType.CO2, value=1.0, unit="test", source="test", category="test")

        with pytest.raises(ValueError, match="Calculation must have at least one result"):
            CalculationRecord(
                calculation_id="test",
                activity=activity,
                factors_applied=[factor],
                results=[],
                total_co2e=0.0,
                scope=Scope.SCOPE_1
            )

    def test_negative_total_co2e_raises_error(self):
        """Test that negative total CO2e raises ValueError."""
        activity = ActivityData(activity_type="test", quantity=1.0, unit=Unit.KG)
        factor = EmissionFactor(gas=GasType.CO2, value=1.0, unit="test", source="test", category="test")
        result = EmissionResult(
            gas=GasType.CO2,
            amount=1.0,
            unit=Unit.KG,
            co2_equivalent=1.0,
            scope=Scope.SCOPE_1,
            factor_used=factor,
            activity=activity
        )

        with pytest.raises(ValueError, match="Total CO2e must be non-negative"):
            CalculationRecord(
                calculation_id="test",
                activity=activity,
                factors_applied=[factor],
                results=[result],
                total_co2e=-1.0,
                scope=Scope.SCOPE_1
            )
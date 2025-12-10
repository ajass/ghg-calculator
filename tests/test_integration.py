"""Integration tests for the GHG emissions calculator."""

import pytest
from datetime import datetime

from ghg_emissions.calculator import EmissionCalculator
from ghg_emissions.factors import FactorLoader
from ghg_emissions.models import (
    ActivityData,
    EmissionFactor,
    GasType,
    ReportData,
    Scope,
    Unit,
)
from ghg_emissions.reporting import ReportGenerator


class TestIntegration:
    """Integration tests combining multiple components."""

    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return EmissionCalculator()

    @pytest.fixture
    def factors(self):
        """Create sample emission factors."""
        return [
            EmissionFactor(
                gas=GasType.CO2,
                value=0.429,  # kg CO2 per kWh
                unit="kg CO2 per kWh",
                source="EPA eGRID",
                category="Electricity"
            ),
            EmissionFactor(
                gas=GasType.CH4,
                value=0.0001,  # kg CH4 per kWh
                unit="kg CH4 per kWh",
                source="EPA eGRID",
                category="Electricity"
            ),
            EmissionFactor(
                gas=GasType.CO2,
                value=2.31,  # kg CO2 per gallon
                unit="kg CO2 per gallon",
                source="EPA",
                category="Gasoline"
            )
        ]

    @pytest.fixture
    def activities(self):
        """Create sample activity data."""
        return [
            ActivityData(
                activity_type="Electricity Usage",
                quantity=1000.0,  # kWh
                unit=Unit.KWH,
                description="Office electricity consumption"
            ),
            ActivityData(
                activity_type="Gasoline Consumption",
                quantity=100.0,  # gallons
                unit=Unit.GALLON,
                description="Company vehicle fuel"
            )
        ]

    def test_full_calculation_workflow(self, calculator, factors, activities):
        """Test complete calculation workflow."""
        # Calculate emissions for electricity
        electricity_factors = [f for f in factors if f.category == "Electricity"]
        electricity_record = calculator.calculate_emissions(
            activity=activities[0],
            factors=electricity_factors,
            scope=Scope.SCOPE_2
        )

        # Calculate emissions for gasoline
        gasoline_factors = [f for f in factors if f.category == "Gasoline"]
        gasoline_record = calculator.calculate_emissions(
            activity=activities[1],
            factors=gasoline_factors,
            scope=Scope.SCOPE_1
        )

        # Verify calculations
        # Electricity: 1000 kWh * (0.429 CO2 + 0.0001 CH4 * 25 GWP) = 429 + 0.25 = 429.25 kg CO2e
        assert abs(electricity_record.total_co2e - 429.25) < 0.01

        # Gasoline: 100 gallons * 2.31 kg CO2 = 231 kg CO2e
        assert abs(gasoline_record.total_co2e - 231.0) < 0.01

    def test_report_generation_workflow(self, calculator, factors, activities):
        """Test report generation workflow."""
        # Calculate emissions
        records = []
        for activity in activities:
            matching_factors = [
                f for f in factors
                if f.category.lower() in activity.activity_type.lower() or
                activity.activity_type.lower().replace(" ", "").startswith(f.category.lower())
            ]
            if matching_factors:
                record = calculator.calculate_emissions(
                    activity=activity,
                    factors=matching_factors,
                    scope=Scope.SCOPE_1
                )
                records.append(record)

        # Create report data
        report_data = ReportData(
            records=records,
            period_start=datetime(2023, 1, 1),
            period_end=datetime(2023, 12, 31),
            organization="Test Company",
            report_title="Annual GHG Emissions Report"
        )

        # Generate reports
        generator = ReportGenerator()

        csv_report = generator.generate_csv(report_data)
        json_report = generator.generate_json(report_data)
        text_report = generator.generate_summary_text(report_data)

        # Verify reports contain expected data
        assert "Test Company" in text_report
        assert "Annual GHG Emissions Report" in text_report

        assert '"organization": "Test Company"' in json_report

        assert 'Activity Type' in csv_report
        assert 'Electricity Usage' in csv_report

    def test_audit_trail_integrity(self, calculator, factors, activities):
        """Test that audit trail maintains data integrity."""
        record = calculator.calculate_emissions(
            activity=activities[0],
            factors=factors[:2],  # Electricity factors
            scope=Scope.SCOPE_2
        )

        # Verify audit trail components
        assert record.calculation_id is not None
        assert record.activity == activities[0]
        assert len(record.factors_applied) == 2
        assert len(record.results) == 2
        assert record.calculated_at is not None

        # Verify CO2e calculation matches sum of results
        total_from_results = sum(r.co2_equivalent for r in record.results)
        assert abs(record.total_co2e - total_from_results) < 0.001
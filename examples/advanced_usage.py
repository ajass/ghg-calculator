"""Advanced example showing plugin usage and custom factors."""

from datetime import datetime
from pathlib import Path

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
from ghg_emissions.plugins import FactorProvider, PluginManager
from ghg_emissions.reporting import ReportGenerator


class CustomFactorProvider(FactorProvider):
    """Example custom factor provider."""

    @property
    def name(self):
        return "custom_provider"

    @property
    def version(self):
        return "1.0.0"

    def get_factors(self, category=None):
        """Provide custom emission factors."""
        custom_factors = [
            EmissionFactor(
                gas=GasType.CO2,
                value=0.35,  # Lower carbon grid
                unit="kg CO2 per kWh",
                source="Custom Renewable Grid",
                category="Electricity",
                description="Renewable energy grid factors"
            ),
            EmissionFactor(
                gas=GasType.CH4,
                value=0.00005,  # Lower methane leakage
                unit="kg CH4 per kWh",
                source="Custom Natural Gas",
                category="Natural Gas",
                description="Efficient natural gas distribution"
            )
        ]

        if category:
            return [f for f in custom_factors if f.category.lower() == category.lower()]
        return custom_factors

    def get_categories(self):
        """Return supported categories."""
        return ["Electricity", "Natural Gas"]


def main():
    """Demonstrate advanced usage with plugins."""

    # Initialize components
    calculator = EmissionCalculator()
    generator = ReportGenerator()

    # Set up plugin manager
    manager = PluginManager()
    custom_provider = CustomFactorProvider()
    manager.register_factor_provider(custom_provider)

    print(f"Registered factor providers: {manager.list_factor_providers()}")

    # Load standard factors
    loader = FactorLoader()
    try:
        standard_factors = loader.load_standard_factors()
    except FileNotFoundError:
        print("Standard factors not available, using only custom factors")
        standard_factors = []

    # Get factors from plugins
    plugin_factors = manager.get_all_factors()
    all_factors = standard_factors + plugin_factors

    print(f"Total factors available: {len(all_factors)}")

    # Define activities
    activities = [
        ActivityData(
            activity_type="Electricity Usage",
            quantity=5000.0,
            unit=Unit.KWH,
            description="Data center electricity with renewable mix"
        ),
        ActivityData(
            activity_type="Natural Gas Usage",
            quantity=100000.0,  # 100,000 kWh equivalent
            unit=Unit.KWH,
            description="Heating and cooling energy"
        )
    ]

    # Calculate emissions
    records = []
    for activity in activities:
        # Try to find factors for this activity
        matching_factors = [
            f for f in all_factors
            if f.category.lower() in activity.activity_type.lower().replace(" usage", "")
        ]

        if not matching_factors:
            # Fallback to any electricity factors for demo
            matching_factors = [f for f in all_factors if "electricity" in f.category.lower()]

        if matching_factors:
            record = calculator.calculate_emissions(
                activity=activity,
                factors=matching_factors,
                scope=Scope.SCOPE_2
            )
            records.append(record)
            print(f"{activity.activity_type}: {record.total_co2e:.2f} kg CO2e")
        else:
            print(f"No suitable factors found for {activity.activity_type}")

    # Generate comprehensive report
    if records:
        report_data = ReportData(
            records=records,
            period_start=datetime(2023, 1, 1),
            period_end=datetime(2023, 12, 31),
            organization="Tech Company Inc.",
            report_title="Q1 2023 GHG Emissions Assessment",
            metadata={
                "reporting_standard": "GHG Protocol",
                "gwp_source": "IPCC AR5",
                "custom_factors_used": "Renewable grid mix"
            }
        )

        # Generate and display summary
        summary = generator.generate_summary_text(report_data)
        print("\n" + "="*50)
        print("GHG EMISSIONS SUMMARY")
        print("="*50)
        print(summary)

        # Save detailed reports
        generator.save_report(report_data, "advanced_report", format="json")
        print("\nDetailed report saved as advanced_report.json")

        # Show factor sources used
        print("\nEmission Factors Used:")
        all_sources = set()
        for record in records:
            for factor in record.factors_applied:
                all_sources.add(f"{factor.category}: {factor.source}")
        for source in sorted(all_sources):
            print(f"  - {source}")

    else:
        print("No calculations performed")


if __name__ == "__main__":
    main()
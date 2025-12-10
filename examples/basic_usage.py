"""Example usage of the GHG Emissions Calculator."""

from datetime import datetime

from ghg_emissions.calculator import EmissionCalculator
from ghg_emissions.factors import FactorLoader
from ghg_emissions.models import ActivityData, ReportData, Scope, Unit
from ghg_emissions.reporting import ReportGenerator


def main():
    """Demonstrate basic usage of the GHG emissions calculator."""

    # Initialize components
    calculator = EmissionCalculator()
    loader = FactorLoader()
    generator = ReportGenerator()

    # Load standard emission factors
    try:
        factors = loader.load_standard_factors()
        print(f"Loaded {len(factors)} emission factors")
    except FileNotFoundError:
        print("Standard factors not found, using sample factors")
        # Create sample factors for demonstration
        from ghg_emissions.models import EmissionFactor, GasType
        factors = [
            EmissionFactor(
                gas=GasType.CO2,
                value=0.429,
                unit="kg CO2 per kWh",
                source="EPA eGRID",
                category="Electricity",
                description="US average grid electricity"
            ),
            EmissionFactor(
                gas=GasType.CO2,
                value=2.31,
                unit="kg CO2 per gallon",
                source="EPA",
                category="Gasoline",
                description="Gasoline combustion"
            )
        ]

    # Define activities
    activities = [
        ActivityData(
            activity_type="Electricity Usage",
            quantity=10000.0,  # 10,000 kWh
            unit=Unit.KWH,
            description="Annual office electricity consumption"
        ),
        ActivityData(
            activity_type="Gasoline Consumption",
            quantity=5000.0,  # 5,000 gallons
            unit=Unit.GALLON,
            description="Company vehicle fuel"
        )
    ]

    # Calculate emissions for each activity
    records = []
    for activity in activities:
        # Find matching factors
        matching_factors = [
            f for f in factors
            if f.category.lower() in activity.activity_type.lower()
        ]

        if matching_factors:
            record = calculator.calculate_emissions(
                activity=activity,
                factors=matching_factors,
                scope=Scope.SCOPE_1 if "gasoline" in activity.activity_type.lower() else Scope.SCOPE_2
            )
            records.append(record)
            print(f"{activity.activity_type}: {record.total_co2e:.2f} kg CO2e")
        else:
            print(f"No factors found for {activity.activity_type}")

    # Generate reports
    if records:
        report_data = ReportData(
            records=records,
            period_start=datetime(2023, 1, 1),
            period_end=datetime(2023, 12, 31),
            organization="Example Company",
            report_title="Annual GHG Emissions Report"
        )

        # Generate different report formats
        print("\n=== CSV Report ===")
        csv_report = generator.generate_csv(report_data)
        print(csv_report[:500] + "..." if len(csv_report) > 500 else csv_report)

        print("\n=== Summary Report ===")
        summary = generator.generate_summary_text(report_data)
        print(summary)

        # Save reports to files
        generator.save_report(report_data, "example_report", format="csv")
        generator.save_report(report_data, "example_report", format="json")
        print("\nReports saved as example_report.csv and example_report.json")
    else:
        print("No calculations to report")


if __name__ == "__main__":
    main()
"""Command-line interface for GHG Emissions Calculator."""

import argparse
import sys
from datetime import datetime

from ghg_emissions.calculator import EmissionCalculator
from ghg_emissions.factors import FactorLoader
from ghg_emissions.models import ActivityData, ReportData, Scope, Unit
from ghg_emissions.reporting import ReportGenerator


def create_parser():
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="Calculate greenhouse gas emissions from activity data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ghg-calculator --activity "Electricity Usage" --quantity 1000 --unit kWh
  ghg-calculator -a "Gasoline Consumption" -q 500 -u gallon -s scope_1
  ghg-calculator --activity "Natural Gas" --quantity 10000 --unit MJ --format csv --output report.csv
        """
    )

    parser.add_argument(
        "-a", "--activity",
        required=True,
        help="Type of activity (e.g., 'Electricity Usage', 'Gasoline Consumption')"
    )

    parser.add_argument(
        "-q", "--quantity",
        type=float,
        required=True,
        help="Quantity of the activity"
    )

    parser.add_argument(
        "-u", "--unit",
        required=True,
        choices=[u.value for u in Unit],
        help="Unit of measurement"
    )

    parser.add_argument(
        "-d", "--description",
        help="Optional description of the activity"
    )

    parser.add_argument(
        "-s", "--scope",
        choices=["scope_1", "scope_2", "scope_3"],
        default="scope_2",
        help="GHG Protocol scope (default: scope_2)"
    )

    parser.add_argument(
        "-f", "--format",
        choices=["text", "csv", "json"],
        default="text",
        help="Output format (default: text)"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file path (if not specified, prints to console)"
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        # Initialize components
        calculator = EmissionCalculator()
        loader = FactorLoader()
        generator = ReportGenerator()

        # Load emission factors
        try:
            factors = loader.load_standard_factors()
            print(f"Loaded {len(factors)} emission factors")
        except FileNotFoundError:
            print("Warning: Standard factors not found, using sample factors")
            # Create basic sample factors
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
                ),
                EmissionFactor(
                    gas=GasType.CO2,
                    value=0.053,
                    unit="kg CO2 per MJ",
                    source="EPA",
                    category="Natural Gas",
                    description="Natural gas combustion"
                )
            ]

        # Create activity data
        activity = ActivityData(
            activity_type=args.activity,
            quantity=args.quantity,
            unit=Unit(args.unit),
            description=args.description
        )

        # Determine scope
        scope_map = {
            "scope_1": Scope.SCOPE_1,
            "scope_2": Scope.SCOPE_2,
            "scope_3": Scope.SCOPE_3
        }
        scope = scope_map[args.scope]

        # Find matching factors
        matching_factors = []
        for factor in factors:
            if factor.category.lower() in args.activity.lower():
                matching_factors.append(factor)

        if not matching_factors:
            # Try broader matching
            activity_lower = args.activity.lower()
            for factor in factors:
                if any(word in activity_lower for word in factor.category.lower().split()):
                    matching_factors.append(factor)

        if not matching_factors:
            print(f"Error: No emission factors found for activity type '{args.activity}'")
            print("Available categories:", [f.category for f in factors])
            sys.exit(1)

        # Calculate emissions
        record = calculator.calculate_emissions(
            activity=activity,
            factors=matching_factors,
            scope=scope
        )

        # Generate output
        if args.format == "text":
            # Simple text output
            output = f"""
Activity: {args.activity}
Quantity: {args.quantity} {args.unit}
Scope: {scope.value}
Total CO2e: {record.total_co2e:.2f} kg

Factors applied:
"""
            for factor in record.factors_applied:
                output += f"- {factor.category}: {factor.value} {factor.unit} ({factor.source})\n"
        elif args.format == "csv":
            # Generate CSV report
            report_data = ReportData(
                records=[record],
                period_start=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                period_end=datetime.now(),
                organization="CLI Calculation",
                report_title=f"Emissions for {args.activity}"
            )
            output = generator.generate_csv(report_data)
        elif args.format == "json":
            # Generate JSON report
            report_data = ReportData(
                records=[record],
                period_start=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                period_end=datetime.now(),
                organization="CLI Calculation",
                report_title=f"Emissions for {args.activity}"
            )
            output = generator.generate_json(report_data)
        else:
            output = "Unsupported format"

        # Output result
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Report saved to {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
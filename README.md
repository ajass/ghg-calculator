# GHG Emissions Calculator

A modular, accurate, and extensible Python application for calculating greenhouse gas emissions using standard emission factors with clear, auditable reporting outputs.

## Features

- **Modular Architecture**: Separate packages for factors, calculation, reporting, and plugins
- **Standard Factors**: Built-in EPA and IPCC emission factors for common activities
- **Accurate Calculations**: Proper GWP (Global Warming Potential) handling for CO2, CH4, N2O
- **Multiple Report Formats**: CSV, JSON, PDF, and text summary reports
- **Audit Trail**: Complete traceability of calculations with timestamps and sources
- **Extensible**: Plugin system for custom factors and calculators
- **Type Safe**: Full type hints and data validation

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

### Command Line Interface

For quick calculations, use the command-line tool:

```bash
# Install the package
pip install -e .

# Calculate electricity emissions
ghg-calculator --activity "Electricity Usage" --quantity 1000 --unit kWh

# Calculate gasoline consumption
ghg-calculator --activity "Gasoline Consumption" --quantity 500 --unit gallon --scope scope_1

# Generate CSV report
ghg-calculator --activity "Natural Gas" --quantity 10000 --unit MJ --format csv --output report.csv
```

### Python API

For programmatic usage:

```python
from ghg_emissions.calculator import EmissionCalculator
from ghg_emissions.factors import FactorLoader
from ghg_emissions.models import ActivityData, Scope, Unit
from ghg_emissions.reporting import ReportGenerator

# Load standard emission factors
loader = FactorLoader()
factors = loader.load_standard_factors()

# Create calculator
calculator = EmissionCalculator()

# Define activity (e.g., electricity usage)
activity = ActivityData(
    activity_type="Electricity Usage",
    quantity=1000.0,  # 1000 kWh
    unit=Unit.KWH,
    description="Office building electricity consumption"
)

# Calculate emissions
record = calculator.calculate_emissions(
    activity=activity,
    factors=[f for f in factors if f.category == "Electricity"],
    scope=Scope.SCOPE_2
)

print(f"Total CO2e emissions: {record.total_co2e} kg")

# Generate report
from ghg_emissions.models import ReportData
from datetime import datetime

report_data = ReportData(
    records=[record],
    period_start=datetime(2023, 1, 1),
    period_end=datetime(2023, 12, 31),
    organization="My Company",
    report_title="Annual GHG Report"
)

generator = ReportGenerator()
csv_report = generator.generate_csv(report_data)
print(csv_report)
```

## Architecture

### Core Components

- **`models.py`**: Data structures using dataclasses with validation
- **`calculator/`**: Emission calculation logic with GWP handling
- **`factors/`**: Factor loading from CSV/JSON sources
- **`reporting/`**: Multi-format report generation
- **`plugins/`**: Extensible plugin system

### Data Flow

1. **Input**: Activity data (quantity, unit, type)
2. **Factors**: Load emission factors from sources
3. **Calculation**: Apply factors with GWP conversion
4. **Results**: Generate audit trail and CO2e totals
5. **Reports**: Export in multiple formats

## API Reference

### Models

#### EmissionFactor
Represents an emission factor with validation.

```python
factor = EmissionFactor(
    gas=GasType.CO2,
    value=0.5,
    unit="kg CO2 per kWh",
    source="EPA",
    category="Electricity"
)
```

#### ActivityData
Represents activity data for calculation.

```python
activity = ActivityData(
    activity_type="Electricity",
    quantity=1000.0,
    unit=Unit.KWH
)
```

#### CalculationRecord
Audit trail for emissions calculations.

### Calculator

#### EmissionCalculator
Main calculator class.

```python
calculator = EmissionCalculator()
record = calculator.calculate_emissions(activity, factors, scope)
```

### Factors

#### FactorLoader
Loads emission factors from files.

```python
loader = FactorLoader()
factors = loader.load_standard_factors()
```

### Reporting

#### ReportGenerator
Generates reports in multiple formats.

```python
generator = ReportGenerator()
csv = generator.generate_csv(report_data)
pdf = generator.generate_pdf(report_data)
```

## Supported Gases and Factors

- **CO2**: Carbon dioxide
- **CH4**: Methane (GWP = 25)
- **N2O**: Nitrous oxide (GWP = 298)

Built-in factors include:
- Electricity (grid average)
- Natural gas combustion
- Gasoline/diesel fuel
- Coal combustion
- Business travel
- Waste (landfill methane)

## Extensibility

### Custom Factors

Add custom emission factors via CSV or JSON files, or implement `FactorProvider` plugins.

### Plugins

Extend functionality with plugins:

```python
from ghg_emissions.plugins import FactorProvider, PluginManager

class MyFactorProvider(FactorProvider):
    @property
    def name(self):
        return "my_provider"

    def get_factors(self, category=None):
        # Return custom factors
        return [...]

# Register plugin
manager = PluginManager()
manager.register_factor_provider(MyFactorProvider())
```

## Testing

Run the test suite:

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Standards Compliance

- Uses IPCC AR5 Global Warming Potentials
- Follows GHG Protocol Scope definitions
- EPA emission factors where applicable
- ISO standards for data validation
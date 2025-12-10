## Task 02: Define core data structures with dataclasses

### Objective
Define the core data structures using Python dataclasses for type safety and immutability.

### Deliverables
- GasType, Unit, Scope enums
- EmissionFactor dataclass with validation
- ActivityData dataclass for input data
- EmissionResult dataclass for calculation outputs
- CalculationRecord dataclass for audit trails
- ReportData dataclass for reporting

### Status
Completed - Created ghg_emissions/models.py with:
- Enums for gas types, units, and scopes
- Dataclasses with validation in __post_init__
- Type hints and proper imports
- Audit trail support with timestamps
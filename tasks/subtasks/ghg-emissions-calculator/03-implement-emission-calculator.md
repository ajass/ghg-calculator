## Task 03: Implement core emission calculation logic

### Objective
Implement the EmissionCalculator class with methods for calculating emissions from activity data using emission factors.

### Deliverables
- EmissionCalculator class in ghg_emissions/calculator/calculator.py
- Support for multiple gases with GWP factors
- Calculation methods for single and multiple activities
- Audit trail with CalculationRecord
- Unit handling and CO2 equivalent calculations

### Status
Completed - Implemented EmissionCalculator with:
- GWP factors for CO2, CH4, N2O (IPCC AR5 values)
- calculate_emissions() method for single activity
- calculate_multiple_activities() method
- Proper validation and audit trail generation
- Extensible GWP factor updates
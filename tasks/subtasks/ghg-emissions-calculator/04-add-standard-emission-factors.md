## Task 04: Add standard emission factors data

### Objective
Create standard emission factors data and loading functionality.

### Deliverables
- factors.csv with standard EPA emission factors
- FactorLoader class in ghg_emissions/factors/loader.py
- Support for loading from CSV/JSON
- Methods for filtering factors by category, gas, or search

### Status
Completed - Added standard factors data with:
- CSV file with EPA factors for electricity, fuels, travel, waste
- FactorLoader class with multiple loading methods
- Search and filtering capabilities
- Error handling for invalid data
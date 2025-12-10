## Task 06: Add extensible plugin system for custom factors

### Objective
Implement a plugin system using entry points for extending the calculator with custom factors and calculators.

### Deliverables
- Base classes FactorProvider and CalculatorPlugin in plugins/base.py
- PluginManager class for managing loaded plugins
- Plugin discovery using importlib.metadata entry points
- Support for loading plugins from modules

### Status
Completed - Added plugin system with:
- Abstract base classes for factors and calculators
- PluginManager for registration and discovery
- Entry points configuration in pyproject.toml
- Discovery functions for automatic loading
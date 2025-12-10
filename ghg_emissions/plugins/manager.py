"""Plugin discovery and loading."""

import importlib.metadata
from typing import List

from .base import CalculatorPlugin, FactorProvider, PluginManager


def discover_plugins() -> PluginManager:
    """Discover and load plugins using entry points."""
    manager = PluginManager()

    # Discover factor providers
    try:
        for entry_point in importlib.metadata.entry_points(group='ghg_emissions.factors'):
            try:
                provider_class = entry_point.load()
                if issubclass(provider_class, FactorProvider):
                    # Assume provider_class is instantiable
                    provider = provider_class()
                    manager.register_factor_provider(provider)
                else:
                    print(f"Warning: {entry_point.name} is not a FactorProvider subclass")
            except Exception as e:
                print(f"Error loading factor provider {entry_point.name}: {e}")
    except Exception as e:
        print(f"Error discovering factor providers: {e}")

    # Discover calculator plugins
    try:
        for entry_point in importlib.metadata.entry_points(group='ghg_emissions.calculators'):
            try:
                plugin_class = entry_point.load()
                if issubclass(plugin_class, CalculatorPlugin):
                    plugin = plugin_class()
                    manager.register_calculator_plugin(plugin)
                else:
                    print(f"Warning: {entry_point.name} is not a CalculatorPlugin subclass")
            except Exception as e:
                print(f"Error loading calculator plugin {entry_point.name}: {e}")
    except Exception as e:
        print(f"Error discovering calculator plugins: {e}")

    return manager


def load_plugin_from_module(module_name: str, manager: PluginManager):
    """Load a plugin from a Python module."""
    try:
        module = __import__(module_name, fromlist=[''])
        # Look for plugin classes in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type):
                if issubclass(attr, FactorProvider) and attr != FactorProvider:
                    provider = attr()
                    manager.register_factor_provider(provider)
                elif issubclass(attr, CalculatorPlugin) and attr != CalculatorPlugin:
                    plugin = attr()
                    manager.register_calculator_plugin(plugin)
    except Exception as e:
        print(f"Error loading plugin from module {module_name}: {e}")


# Global plugin manager instance
_default_manager = None

def get_plugin_manager() -> PluginManager:
    """Get the default plugin manager, discovering plugins if needed."""
    global _default_manager
    if _default_manager is None:
        _default_manager = discover_plugins()
    return _default_manager
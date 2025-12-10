"""Plugin system for extending GHG emissions calculator."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ..models import EmissionFactor


class FactorProvider(ABC):
    """Abstract base class for emission factor providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @abstractmethod
    def get_factors(self, category: Optional[str] = None) -> List[EmissionFactor]:
        """Get emission factors provided by this plugin."""
        pass

    @abstractmethod
    def get_categories(self) -> List[str]:
        """Get list of categories provided by this plugin."""
        pass


class CalculatorPlugin(ABC):
    """Abstract base class for calculator plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @abstractmethod
    def calculate_custom(
        self,
        activity_data: Dict,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """Perform custom calculation."""
        pass


class PluginManager:
    """Manager for loading and managing plugins."""

    def __init__(self):
        """Initialize plugin manager."""
        self.factor_providers: Dict[str, FactorProvider] = {}
        self.calculator_plugins: Dict[str, CalculatorPlugin] = {}

    def register_factor_provider(self, provider: FactorProvider):
        """Register a factor provider plugin."""
        self.factor_providers[provider.name] = provider

    def register_calculator_plugin(self, plugin: CalculatorPlugin):
        """Register a calculator plugin."""
        self.calculator_plugins[plugin.name] = plugin

    def get_all_factors(self, category: Optional[str] = None) -> List[EmissionFactor]:
        """Get factors from all registered providers."""
        all_factors = []
        for provider in self.factor_providers.values():
            factors = provider.get_factors(category)
            all_factors.extend(factors)
        return all_factors

    def get_factors_by_provider(self, provider_name: str) -> List[EmissionFactor]:
        """Get factors from a specific provider."""
        if provider_name not in self.factor_providers:
            return []
        return self.factor_providers[provider_name].get_factors()

    def get_available_categories(self) -> List[str]:
        """Get all available categories from providers."""
        categories = set()
        for provider in self.factor_providers.values():
            categories.update(provider.get_categories())
        return sorted(list(categories))

    def list_factor_providers(self) -> List[str]:
        """List names of registered factor providers."""
        return list(self.factor_providers.keys())

    def list_calculator_plugins(self) -> List[str]:
        """List names of registered calculator plugins."""
        return list(self.calculator_plugins.keys())

    def get_calculator_plugin(self, name: str) -> Optional[CalculatorPlugin]:
        """Get a calculator plugin by name."""
        return self.calculator_plugins.get(name)
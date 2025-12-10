"""Core data structures for GHG emissions calculator."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union


class GasType(Enum):
    """Greenhouse gas types."""
    CO2 = "CO2"
    CH4 = "CH4"
    N2O = "N2O"
    CO2E = "CO2e"  # CO2 equivalent


class Unit(Enum):
    """Units for quantities and emissions."""
    KG = "kg"
    TONNE = "tonne"
    LITER = "liter"
    GALLON = "gallon"
    KWH = "kWh"
    MJ = "MJ"
    KM = "km"
    MILE = "mile"


class Scope(Enum):
    """GHG Protocol scopes."""
    SCOPE_1 = "Scope 1"
    SCOPE_2 = "Scope 2"
    SCOPE_3 = "Scope 3"


@dataclass
class EmissionFactor:
    """Emission factor data structure."""
    gas: GasType
    value: float
    unit: str  # e.g., "kg CO2e per unit"
    source: str
    category: str
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None

    def __post_init__(self):
        """Validate emission factor."""
        if self.value < 0:
            raise ValueError("Emission factor value must be non-negative")


@dataclass
class ActivityData:
    """Activity data for emissions calculation."""
    activity_type: str
    quantity: float
    unit: Unit
    description: Optional[str] = None
    metadata: Dict[str, Union[str, float, int]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate activity data."""
        if self.quantity < 0:
            raise ValueError("Activity quantity must be non-negative")


@dataclass
class EmissionResult:
    """Result of emissions calculation."""
    gas: GasType
    amount: float
    unit: Unit
    co2_equivalent: float  # in kg CO2e
    scope: Scope
    factor_used: EmissionFactor
    activity: ActivityData
    calculated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate emission result."""
        if self.amount < 0:
            raise ValueError("Emission amount must be non-negative")
        if self.co2_equivalent < 0:
            raise ValueError("CO2 equivalent must be non-negative")


@dataclass
class CalculationRecord:
    """Audit trail for emissions calculation."""
    calculation_id: str
    activity: ActivityData
    factors_applied: List[EmissionFactor]
    results: List[EmissionResult]
    total_co2e: float
    scope: Scope
    calculated_by: str = "ghg-emissions"
    calculated_at: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None

    def __post_init__(self):
        """Validate calculation record."""
        if not self.results:
            raise ValueError("Calculation must have at least one result")
        if self.total_co2e < 0:
            raise ValueError("Total CO2e must be non-negative")


@dataclass
class ReportData:
    """Data for generating reports."""
    records: List[CalculationRecord]
    period_start: datetime
    period_end: datetime
    organization: str
    report_title: str
    generated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Union[str, float, int]] = field(default_factory=dict)
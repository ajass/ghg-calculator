"""GUI-specific data models for GHG Emissions Calculator."""

from dataclasses import dataclass
from typing import List, Optional

from ..models import ActivityData, Scope, Unit, EmissionResult


@dataclass
class GUIActivity:
    """GUI representation of an activity."""
    activity_type: str
    quantity: float
    unit: Unit
    scope: Scope
    description: Optional[str] = None

    def to_activity_data(self) -> ActivityData:
        """Convert to ActivityData for calculation."""
        return ActivityData(
            activity_type=self.activity_type,
            quantity=self.quantity,
            unit=self.unit,
            description=self.description
        )


@dataclass
class GUIResult:
    """GUI representation of calculation results."""
    activity: GUIActivity
    total_co2e: float
    breakdown: List[EmissionResult]

    @property
    def formatted_breakdown(self) -> str:
        """Get formatted breakdown string."""
        if not self.breakdown:
            return "No breakdown available"

        lines = []
        for result in self.breakdown:
            lines.append(f"{result.gas.value}: {result.amount:.2f} {result.unit.value} "
                        f"({result.co2_equivalent:.2f} kg CO2e)")

        return "\n".join(lines)
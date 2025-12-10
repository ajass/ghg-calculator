"""Emission calculation logic."""

import uuid
from typing import Dict, List, Optional

from ..models import (
    ActivityData,
    CalculationRecord,
    EmissionFactor,
    EmissionResult,
    GasType,
    Scope,
    Unit,
)


# Global Warming Potentials (GWP) for CO2 equivalent calculations
# Values from IPCC AR5, 100-year horizon
GWP_FACTORS = {
    GasType.CO2: 1.0,
    GasType.CH4: 25.0,
    GasType.N2O: 298.0,
    GasType.CO2E: 1.0,  # Already equivalent
}


class EmissionCalculator:
    """Core calculator for greenhouse gas emissions."""

    def __init__(self, gwp_factors: Optional[Dict[GasType, float]] = None):
        """Initialize calculator with GWP factors."""
        self.gwp_factors = gwp_factors or GWP_FACTORS.copy()

    def calculate_emissions(
        self,
        activity: ActivityData,
        factors: List[EmissionFactor],
        scope: Scope,
        calculation_id: Optional[str] = None,
    ) -> CalculationRecord:
        """
        Calculate emissions for an activity using provided factors.

        Args:
            activity: Activity data to calculate emissions for
            factors: List of emission factors to apply
            scope: GHG Protocol scope for this calculation
            calculation_id: Optional ID for the calculation

        Returns:
            CalculationRecord with results and audit trail
        """
        if not factors:
            raise ValueError("At least one emission factor must be provided")

        if calculation_id is None:
            calculation_id = str(uuid.uuid4())

        results = []
        total_co2e = 0.0

        for factor in factors:
            # Calculate raw emission amount
            emission_amount = activity.quantity * factor.value

            # Calculate CO2 equivalent
            co2_equivalent = emission_amount * self.gwp_factors[factor.gas]

            result = EmissionResult(
                gas=factor.gas,
                amount=emission_amount,
                unit=Unit.KG,  # Assume kg for now, could be parameterized
                co2_equivalent=co2_equivalent,
                scope=scope,
                factor_used=factor,
                activity=activity,
            )

            results.append(result)
            total_co2e += co2_equivalent

        record = CalculationRecord(
            calculation_id=calculation_id,
            activity=activity,
            factors_applied=factors,
            results=results,
            total_co2e=total_co2e,
            scope=scope,
        )

        return record

    def calculate_multiple_activities(
        self,
        activities: List[ActivityData],
        factors: List[EmissionFactor],
        scope: Scope,
    ) -> List[CalculationRecord]:
        """
        Calculate emissions for multiple activities.

        Args:
            activities: List of activity data
            factors: List of emission factors (will be matched by category/type)
            scope: GHG Protocol scope

        Returns:
            List of calculation records
        """
        records = []

        for activity in activities:
            # Find matching factors for this activity type
            matching_factors = [
                f for f in factors
                if f.category.lower() in activity.activity_type.lower() or
                activity.activity_type.lower() in f.category.lower()
            ]

            if not matching_factors:
                # Use all factors if no specific match (could be improved)
                matching_factors = factors

            record = self.calculate_emissions(activity, matching_factors, scope)
            records.append(record)

        return records

    def get_supported_gases(self) -> List[GasType]:
        """Get list of supported greenhouse gases."""
        return list(self.gwp_factors.keys())

    def update_gwp_factors(self, factors: Dict[GasType, float]):
        """Update global warming potential factors."""
        self.gwp_factors.update(factors)
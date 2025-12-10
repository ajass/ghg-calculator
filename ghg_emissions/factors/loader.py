"""Emission factors loading and management."""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from ..models import EmissionFactor, GasType


class FactorLoader:
    """Loader for emission factors from various sources."""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize loader with data directory."""
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir

    def load_from_csv(self, filename: str = "factors.csv") -> List[EmissionFactor]:
        """Load emission factors from CSV file."""
        filepath = self.data_dir / filename
        factors = []

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    gas = GasType(row['gas'])
                    factor = EmissionFactor(
                        gas=gas,
                        value=float(row['value']),
                        unit=row['unit'],
                        source=row['source'],
                        category=row['category'],
                        description=row.get('description'),
                    )
                    factors.append(factor)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid factor row: {row} - {e}")
                    continue

        return factors

    def load_from_json(self, filename: str = "factors.json") -> List[EmissionFactor]:
        """Load emission factors from JSON file."""
        filepath = self.data_dir / filename
        factors = []

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            try:
                gas = GasType(item['gas'])
                factor = EmissionFactor(
                    gas=gas,
                    value=float(item['value']),
                    unit=item['unit'],
                    source=item['source'],
                    category=item['category'],
                    description=item.get('description'),
                )
                factors.append(factor)
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping invalid factor item: {item} - {e}")
                continue

        return factors

    def load_standard_factors(self) -> List[EmissionFactor]:
        """Load standard emission factors from default sources."""
        factors = []

        # Try CSV first
        csv_file = self.data_dir / "factors.csv"
        if csv_file.exists():
            factors.extend(self.load_from_csv())

        # Try JSON
        json_file = self.data_dir / "factors.json"
        if json_file.exists():
            factors.extend(self.load_from_json())

        if not factors:
            raise FileNotFoundError(f"No factor files found in {self.data_dir}")

        return factors

    def get_factors_by_category(self, category: str) -> List[EmissionFactor]:
        """Get factors for a specific category."""
        all_factors = self.load_standard_factors()
        return [f for f in all_factors if f.category.lower() == category.lower()]

    def get_factors_by_gas(self, gas: GasType) -> List[EmissionFactor]:
        """Get factors for a specific gas."""
        all_factors = self.load_standard_factors()
        return [f for f in all_factors if f.gas == gas]

    def search_factors(self, query: str) -> List[EmissionFactor]:
        """Search factors by category or description."""
        all_factors = self.load_standard_factors()
        query_lower = query.lower()
        return [
            f for f in all_factors
            if query_lower in f.category.lower() or
            (f.description and query_lower in f.description.lower())
        ]
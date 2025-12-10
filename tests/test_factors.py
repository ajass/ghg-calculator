"""Tests for factor loading."""

import pytest
import tempfile
import csv
import json
from pathlib import Path

from ghg_emissions.factors import FactorLoader
from ghg_emissions.models import EmissionFactor, GasType


class TestFactorLoader:
    """Test FactorLoader class."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_csv_content(self):
        """Sample CSV content for testing."""
        return """category,gas,value,unit,source,description
Electricity,CO2,0.5,kg CO2 per kWh,Test Source,Electricity emissions
Fuel,CH4,0.001,kg CH4 per liter,Test Source,Fuel methane"""

    @pytest.fixture
    def sample_json_content(self):
        """Sample JSON content for testing."""
        return [
            {
                "category": "Electricity",
                "gas": "CO2",
                "value": 0.5,
                "unit": "kg CO2 per kWh",
                "source": "Test Source",
                "description": "Electricity emissions"
            }
        ]

    def test_load_from_csv(self, temp_data_dir, sample_csv_content):
        """Test loading factors from CSV."""
        csv_file = temp_data_dir / "factors.csv"
        csv_file.write_text(sample_csv_content)

        loader = FactorLoader(temp_data_dir)
        factors = loader.load_from_csv()

        assert len(factors) == 2
        assert factors[0].gas == GasType.CO2
        assert factors[0].value == 0.5
        assert factors[1].gas == GasType.CH4
        assert factors[1].value == 0.001

    def test_load_from_json(self, temp_data_dir, sample_json_content):
        """Test loading factors from JSON."""
        json_file = temp_data_dir / "factors.json"
        json_file.write_text(json.dumps(sample_json_content))

        loader = FactorLoader(temp_data_dir)
        factors = loader.load_from_json()

        assert len(factors) == 1
        assert factors[0].gas == GasType.CO2
        assert factors[0].value == 0.5

    def test_load_standard_factors_no_files(self, temp_data_dir):
        """Test loading when no factor files exist."""
        loader = FactorLoader(temp_data_dir)

        with pytest.raises(FileNotFoundError):
            loader.load_standard_factors()

    def test_get_factors_by_category(self, temp_data_dir, sample_csv_content):
        """Test filtering factors by category."""
        csv_file = temp_data_dir / "factors.csv"
        csv_file.write_text(sample_csv_content)

        loader = FactorLoader(temp_data_dir)
        electricity_factors = loader.get_factors_by_category("Electricity")

        assert len(electricity_factors) == 1
        assert electricity_factors[0].category == "Electricity"

    def test_get_factors_by_gas(self, temp_data_dir, sample_csv_content):
        """Test filtering factors by gas type."""
        csv_file = temp_data_dir / "factors.csv"
        csv_file.write_text(sample_csv_content)

        loader = FactorLoader(temp_data_dir)
        co2_factors = loader.get_factors_by_gas(GasType.CO2)

        assert len(co2_factors) == 1
        assert co2_factors[0].gas == GasType.CO2

    def test_search_factors(self, temp_data_dir, sample_csv_content):
        """Test searching factors by query."""
        csv_file = temp_data_dir / "factors.csv"
        csv_file.write_text(sample_csv_content)

        loader = FactorLoader(temp_data_dir)
        results = loader.search_factors("Electricity")

        assert len(results) == 1
        assert "Electricity" in results[0].category

    def test_invalid_csv_data(self, temp_data_dir):
        """Test handling of invalid CSV data."""
        invalid_csv = """category,gas,value,unit,source
Electricity,INVALID_GAS,0.5,kg per kWh,Test"""
        csv_file = temp_data_dir / "factors.csv"
        csv_file.write_text(invalid_csv)

        loader = FactorLoader(temp_data_dir)
        factors = loader.load_from_csv()

        # Should skip invalid row
        assert len(factors) == 0
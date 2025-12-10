"""Tests for GHG Emissions Calculator GUI."""

import pytest
from unittest.mock import Mock, patch

from ghg_emissions.models import Unit, Scope
from ghg_emissions.gui.models import GUIActivity
from ghg_emissions.gui.utils import validate_activity_input, format_emission_result


class TestGUIUtils:
    """Test GUI utility functions."""

    def test_validate_activity_input_valid(self):
        """Test validation with valid input."""
        result = validate_activity_input(
            activity_type="Electricity",
            quantity="1000",
            unit="kWh",
            scope="Scope 2",
            description="Office electricity"
        )

        assert isinstance(result, GUIActivity)
        assert result.activity_type == "Electricity"
        assert result.quantity == 1000.0
        assert result.unit == Unit.KWH
        assert result.scope == Scope.SCOPE_2
        assert result.description == "Office electricity"

    def test_validate_activity_input_missing_required(self):
        """Test validation with missing required fields."""
        with pytest.raises(ValueError, match="Activity type is required"):
            validate_activity_input("", "1000", "kWh", "Scope 2", "")

    def test_validate_activity_input_invalid_quantity(self):
        """Test validation with invalid quantity."""
        with pytest.raises(ValueError, match="Quantity must be a valid number"):
            validate_activity_input("Electricity", "invalid", "kWh", "Scope 2", "")

    def test_validate_activity_input_negative_quantity(self):
        """Test validation with negative quantity."""
        with pytest.raises(ValueError, match="Quantity must be non-negative"):
            validate_activity_input("Electricity", "-100", "kWh", "Scope 2", "")

    def test_validate_activity_input_invalid_unit(self):
        """Test validation with invalid unit."""
        with pytest.raises(ValueError, match="Invalid unit"):
            validate_activity_input("Electricity", "1000", "invalid", "Scope 2", "")

    def test_validate_activity_input_invalid_scope(self):
        """Test validation with invalid scope."""
        with pytest.raises(ValueError, match="Invalid scope"):
            validate_activity_input("Electricity", "1000", "kWh", "invalid", "")

    def test_format_emission_result(self):
        """Test emission result formatting."""
        assert format_emission_result(500.5) == "500.50 kg CO2e"
        assert format_emission_result(1500.0) == "1.50 tonnes CO2e"


class TestGUIIntegration:
    """Integration tests for GUI components."""

    @patch('ghg_emissions.gui.app.QApplication')
    @patch('ghg_emissions.gui.app.QMainWindow')
    def test_app_initialization(self, mock_qmainwindow, mock_qapp):
        """Test GUI app initialization."""
        from ghg_emissions.gui.app import GHGCalculatorApp

        # Mock the required components
        mock_window = Mock()
        mock_qmainwindow.return_value = mock_window

        app = GHGCalculatorApp()

        # Verify calculator components are initialized
        assert hasattr(app, 'calculator')
        assert hasattr(app, 'factor_loader')
        assert hasattr(app, 'report_generator')
        assert hasattr(app, 'factors')
        assert hasattr(app, 'activities')
        assert hasattr(app, 'results')

    @patch('ghg_emissions.calculator.EmissionCalculator')
    @patch('ghg_emissions.factors.FactorLoader')
    def test_calculate_emissions_integration(self, mock_factor_loader, mock_calculator):
        """Test integration with calculator."""
        from ghg_emissions.gui.app import GHGCalculatorApp
        from ghg_emissions.models import CalculationRecord, EmissionResult, GasType
        from unittest.mock import MagicMock

        # Mock dependencies
        mock_calc_instance = Mock()
        mock_calculator.return_value = mock_calc_instance

        mock_loader_instance = Mock()
        mock_factor_loader.return_value = mock_loader_instance
        mock_loader_instance.load_standard_factors.return_value = []

        # Create app
        with patch('PyQt6.QtWidgets.QApplication'), \
             patch('PyQt6.QtWidgets.QMainWindow'):
            app = GHGCalculatorApp()

        # Mock calculation record
        mock_record = Mock(spec=CalculationRecord)
        mock_record.total_co2e = 100.0
        mock_record.results = []
        mock_calc_instance.calculate_emissions.return_value = mock_record

        # Add test activity
        app.activities = [
            GUIActivity("Electricity", 1000.0, Unit.KWH, Scope.SCOPE_2, "Test")
        ]

        # Mock the table
        app.results_table = Mock()
        app.results_table.rowCount.return_value = 0
        app.results_table.insertRow = Mock()
        app.results_table.setItem = Mock()

        # Mock total label
        app.total_label = Mock()

        # Call calculate
        app._calculate_emissions()

        # Verify calculator was called
        mock_calc_instance.calculate_emissions.assert_called_once()

        # Verify results were added
        assert len(app.results) == 1
        app.results_table.insertRow.assert_called_once()
        app.total_label.setText.assert_called_once_with("Total CO2e: 100.00 kg")
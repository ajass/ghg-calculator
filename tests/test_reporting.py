"""Tests for report generation."""

import pytest
from datetime import datetime
from io import StringIO

from ghg_emissions.reporting import ReportGenerator
from ghg_emissions.models import (
    ActivityData,
    CalculationRecord,
    EmissionFactor,
    EmissionResult,
    GasType,
    ReportData,
    Scope,
    Unit,
)


class TestReportGenerator:
    """Test ReportGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create report generator instance."""
        return ReportGenerator()

    @pytest.fixture
    def sample_report_data(self):
        """Create sample report data for testing."""
        factor = EmissionFactor(
            gas=GasType.CO2,
            value=0.5,
            unit="kg CO2 per kWh",
            source="Test Source",
            category="Electricity"
        )
        activity = ActivityData(
            activity_type="Electricity Usage",
            quantity=1000.0,
            unit=Unit.KWH
        )
        result = EmissionResult(
            gas=GasType.CO2,
            amount=500.0,
            unit=Unit.KG,
            co2_equivalent=500.0,
            scope=Scope.SCOPE_2,
            factor_used=factor,
            activity=activity
        )
        record = CalculationRecord(
            calculation_id="test-123",
            activity=activity,
            factors_applied=[factor],
            results=[result],
            total_co2e=500.0,
            scope=Scope.SCOPE_2
        )

        return ReportData(
            records=[record],
            period_start=datetime(2023, 1, 1),
            period_end=datetime(2023, 12, 31),
            organization="Test Org",
            report_title="Test GHG Report"
        )

    def test_generate_csv(self, generator, sample_report_data):
        """Test CSV report generation."""
        csv_content = generator.generate_csv(sample_report_data)

        # Check that it's valid CSV
        lines = csv_content.strip().split('\n')
        assert len(lines) == 2  # Header + 1 data row

        # Check header
        assert 'Calculation ID' in lines[0]
        assert 'Activity Type' in lines[0]

        # Check data
        assert 'test-123' in lines[1]
        assert 'Electricity Usage' in lines[1]

    def test_generate_json(self, generator, sample_report_data):
        """Test JSON report generation."""
        json_content = generator.generate_json(sample_report_data)
        data = json.loads(json_content)

        assert data['report_title'] == 'Test GHG Report'
        assert data['organization'] == 'Test Org'
        assert len(data['records']) == 1
        assert data['records'][0]['calculation_id'] == 'test-123'
        assert data['records'][0]['total_co2e'] == 500.0

    def test_generate_summary_text(self, generator, sample_report_data):
        """Test text summary generation."""
        summary = generator.generate_summary_text(sample_report_data)

        assert 'Test GHG Report' in summary
        assert 'Test Org' in summary
        assert '500.0 kg' in summary
        assert 'Electricity Usage' in summary

    def test_generate_pdf(self, generator, sample_report_data):
        """Test PDF report generation."""
        pdf_bytes = generator.generate_pdf(sample_report_data)

        # Check that we got bytes (basic check)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

        # Could check PDF header, but for now just ensure it's not empty

    def test_save_report_csv(self, generator, sample_report_data, tmp_path):
        """Test saving CSV report to file."""
        filename = tmp_path / "test_report"
        generator.save_report(sample_report_data, str(filename), format='csv')

        assert (tmp_path / "test_report.csv").exists()

        with open(tmp_path / "test_report.csv", 'r') as f:
            content = f.read()
            assert 'Calculation ID' in content

    def test_save_report_invalid_format(self, generator, sample_report_data):
        """Test saving with invalid format raises error."""
        with pytest.raises(ValueError, match="Unsupported format"):
            generator.save_report(sample_report_data, "test", format="invalid")
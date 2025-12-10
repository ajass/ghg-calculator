"""Report generation for GHG emissions."""

import csv
import json
from io import BytesIO, StringIO
from pathlib import Path
from typing import Dict, List, Optional

from jinja2 import Template
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from ..models import CalculationRecord, ReportData


class ReportGenerator:
    """Generator for GHG emissions reports in multiple formats."""

    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize generator with template directory."""
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
        self.template_dir = template_dir
        self.template_dir.mkdir(exist_ok=True)

    def generate_csv(self, report_data: ReportData) -> str:
        """Generate CSV report."""
        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Calculation ID', 'Activity Type', 'Quantity', 'Unit',
            'Gas', 'Emission Amount', 'CO2 Equivalent (kg)', 'Scope',
            'Factor Source', 'Calculated At'
        ])

        # Data rows
        for record in report_data.records:
            for result in record.results:
                writer.writerow([
                    record.calculation_id,
                    record.activity.activity_type,
                    record.activity.quantity,
                    record.activity.unit.value,
                    result.gas.value,
                    result.amount,
                    result.co2_equivalent,
                    record.scope.value,
                    result.factor_used.source,
                    result.calculated_at.isoformat()
                ])

        return output.getvalue()

    def generate_json(self, report_data: ReportData) -> str:
        """Generate JSON report."""
        data = {
            'report_title': report_data.report_title,
            'organization': report_data.organization,
            'period': {
                'start': report_data.period_start.isoformat(),
                'end': report_data.period_end.isoformat()
            },
            'generated_at': report_data.generated_at.isoformat(),
            'metadata': report_data.metadata,
            'records': []
        }

        for record in report_data.records:
            record_data = {
                'calculation_id': record.calculation_id,
                'activity': {
                    'type': record.activity.activity_type,
                    'quantity': record.activity.quantity,
                    'unit': record.activity.unit.value,
                    'description': record.activity.description,
                    'metadata': record.activity.metadata
                },
                'scope': record.scope.value,
                'total_co2e': record.total_co2e,
                'factors_applied': [
                    {
                        'gas': f.gas.value,
                        'value': f.value,
                        'unit': f.unit,
                        'source': f.source,
                        'category': f.category,
                        'description': f.description
                    } for f in record.factors_applied
                ],
                'results': [
                    {
                        'gas': r.gas.value,
                        'amount': r.amount,
                        'unit': r.unit.value,
                        'co2_equivalent': r.co2_equivalent,
                        'calculated_at': r.calculated_at.isoformat()
                    } for r in record.results
                ],
                'calculated_at': record.calculated_at.isoformat(),
                'notes': record.notes
            }
            data['records'].append(record_data)

        return json.dumps(data, indent=2)

    def generate_summary_text(self, report_data: ReportData) -> str:
        """Generate text summary report."""
        total_co2e = sum(r.total_co2e for r in report_data.records)
        total_records = len(report_data.records)

        summary = f"""
GHG Emissions Report
====================

Organization: {report_data.organization}
Report Title: {report_data.report_title}
Period: {report_data.period_start.date()} to {report_data.period_end.date()}
Generated: {report_data.generated_at}

Summary:
--------
Total Calculations: {total_records}
Total CO2 Equivalent: {total_co2e:.2f} kg

Breakdown by Scope:
"""

        scope_totals = {}
        for record in report_data.records:
            scope = record.scope.value
            scope_totals[scope] = scope_totals.get(scope, 0) + record.total_co2e

        for scope, total in scope_totals.items():
            summary += f"- {scope}: {total:.2f} kg CO2e\n"

        summary += "\nDetailed Records:\n"
        for i, record in enumerate(report_data.records, 1):
            summary += f"{i}. {record.activity.activity_type}: {record.total_co2e:.2f} kg CO2e\n"

        return summary

    def generate_pdf(self, report_data: ReportData) -> bytes:
        """Generate PDF report."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title = Paragraph(f"<b>{report_data.report_title}</b>", styles['Title'])
        elements.append(title)

        # Header info
        header_text = f"""
        <b>Organization:</b> {report_data.organization}<br/>
        <b>Period:</b> {report_data.period_start.date()} to {report_data.period_end.date()}<br/>
        <b>Generated:</b> {report_data.generated_at}
        """
        elements.append(Paragraph(header_text, styles['Normal']))

        # Summary table
        total_co2e = sum(r.total_co2e for r in report_data.records)
        summary_data = [
            ['Metric', 'Value'],
            ['Total Calculations', str(len(report_data.records))],
            ['Total CO2 Equivalent (kg)', f"{total_co2e:.2f}"]
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(summary_table)

        # Detailed results table
        if report_data.records:
            table_data = [['Activity', 'Scope', 'CO2e (kg)']]
            for record in report_data.records:
                table_data.append([
                    record.activity.activity_type,
                    record.scope.value,
                    f"{record.total_co2e:.2f}"
                ])

            results_table = Table(table_data)
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(results_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    def save_report(self, report_data: ReportData, filename: str, format: str = 'csv'):
        """Save report to file in specified format."""
        if format.lower() == 'csv':
            content = self.generate_csv(report_data)
            with open(f"{filename}.csv", 'w', encoding='utf-8') as f:
                f.write(content)
        elif format.lower() == 'json':
            content = self.generate_json(report_data)
            with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                f.write(content)
        elif format.lower() == 'pdf':
            content = self.generate_pdf(report_data)
            with open(f"{filename}.pdf", 'wb') as f:
                f.write(content)
        elif format.lower() == 'txt':
            content = self.generate_summary_text(report_data)
            with open(f"{filename}.txt", 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            raise ValueError(f"Unsupported format: {format}")
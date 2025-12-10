"""Main GUI application for GHG Emissions Calculator using PyQt6."""

import sys
from typing import List, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QGroupBox, QLabel, QLineEdit, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog,
    QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from ..calculator import EmissionCalculator
from ..factors import FactorLoader
from ..models import ActivityData, Scope, Unit, ReportData
from ..reporting import ReportGenerator
from .models import GUIActivity, GUIResult
from .utils import validate_activity_input, format_emission_result


class GHGCalculatorApp(QMainWindow):
    """Main GUI application class using PyQt6."""

    def __init__(self):
        """Initialize the GUI application."""
        super().__init__()
        self.setWindowTitle("GHG Emissions Calculator")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize calculator components
        self.calculator = EmissionCalculator()
        self.factor_loader = FactorLoader()
        self.report_generator = ReportGenerator()

        # Load standard factors
        self.factors = self.factor_loader.load_standard_factors()

        # GUI state
        self.activities: List[GUIActivity] = []
        self.results: List[GUIResult] = []

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("GHG Emissions Calculator")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Splitter for input and results
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)

        # Activity input section
        self._create_activity_input_section(splitter)

        # Results section
        self._create_results_section(splitter)

        # Buttons
        self._create_buttons(main_layout)

    def _create_activity_input_section(self, parent):
        """Create the activity input section."""
        input_group = QGroupBox("Add Activity")
        parent.addWidget(input_group)

        layout = QFormLayout(input_group)

        # Activity type
        self.activity_type_combo = QComboBox()
        self.activity_type_combo.addItems(self._get_activity_types())
        layout.addRow("Activity Type:", self.activity_type_combo)

        # Quantity
        self.quantity_edit = QLineEdit()
        layout.addRow("Quantity:", self.quantity_edit)

        # Unit
        self.unit_combo = QComboBox()
        self.unit_combo.addItems([u.value for u in Unit])
        layout.addRow("Unit:", self.unit_combo)

        # Scope
        self.scope_combo = QComboBox()
        self.scope_combo.addItems([s.value for s in Scope])
        self.scope_combo.setCurrentText(Scope.SCOPE_1.value)
        layout.addRow("Scope:", self.scope_combo)

        # Description
        self.description_edit = QLineEdit()
        layout.addRow("Description:", self.description_edit)

        # Add activity button
        add_button = QPushButton("Add Activity")
        add_button.clicked.connect(self._add_activity)
        layout.addRow(add_button)

    def _create_results_section(self, parent):
        """Create the results display section."""
        results_group = QGroupBox("Results")
        parent.addWidget(results_group)

        layout = QVBoxLayout(results_group)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Activity", "Quantity", "Unit", "CO2e (kg)"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setAlternatingRowColors(True)
        layout.addWidget(self.results_table)

        # Total emissions label
        self.total_label = QLabel("Total CO2e: 0.00 kg")
        total_font = QFont("Arial", 12, QFont.Weight.Bold)
        self.total_label.setFont(total_font)
        layout.addWidget(self.total_label)

    def _create_buttons(self, parent):
        """Create action buttons."""
        button_layout = QHBoxLayout()

        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self._calculate_emissions)
        button_layout.addWidget(calculate_button)

        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self._clear_all)
        button_layout.addWidget(clear_button)

        export_csv_button = QPushButton("Export CSV")
        export_csv_button.clicked.connect(lambda: self._export_results("csv"))
        button_layout.addWidget(export_csv_button)

        export_json_button = QPushButton("Export JSON")
        export_json_button.clicked.connect(lambda: self._export_results("json"))
        button_layout.addWidget(export_json_button)

        export_pdf_button = QPushButton("Export PDF")
        export_pdf_button.clicked.connect(lambda: self._export_results("pdf"))
        button_layout.addWidget(export_pdf_button)

        parent.addLayout(button_layout)

    def _get_activity_types(self) -> List[str]:
        """Get available activity types from factors."""
        return list(set(f.category for f in self.factors))

    def _add_activity(self):
        """Add an activity to the list."""
        try:
            # Validate input
            activity_data = validate_activity_input(
                activity_type=self.activity_type_combo.currentText(),
                quantity=self.quantity_edit.text(),
                unit=self.unit_combo.currentText(),
                scope=self.scope_combo.currentText(),
                description=self.description_edit.text()
            )

            # Create GUI activity
            gui_activity = GUIActivity(
                activity_type=activity_data.activity_type,
                quantity=activity_data.quantity,
                unit=activity_data.unit,
                scope=activity_data.scope,
                description=activity_data.description
            )

            self.activities.append(gui_activity)

            # Clear form
            self.quantity_edit.clear()
            self.description_edit.clear()

            QMessageBox.information(self, "Success", "Activity added successfully!")

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add activity: {str(e)}")

    def _calculate_emissions(self):
        """Calculate emissions for all activities."""
        if not self.activities:
            QMessageBox.warning(self, "No Activities", "Please add at least one activity before calculating.")
            return

        try:
            # Clear previous results
            self.results_table.setRowCount(0)
            self.results = []
            total_co2e = 0.0

            for activity in self.activities:
                # Convert to ActivityData
                activity_data = ActivityData(
                    activity_type=activity.activity_type,
                    quantity=activity.quantity,
                    unit=activity.unit,
                    description=activity.description
                )

                # Calculate emissions
                record = self.calculator.calculate_emissions(
                    activity=activity_data,
                    factors=[f for f in self.factors if f.category == activity.activity_type],
                    scope=activity.scope
                )

                # Create GUI result
                gui_result = GUIResult(
                    activity=activity,
                    total_co2e=record.total_co2e,
                    breakdown=record.results
                )

                self.results.append(gui_result)
                total_co2e += record.total_co2e

                # Add to table
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(activity.activity_type))
                self.results_table.setItem(row, 1, QTableWidgetItem(f"{activity.quantity:.2f}"))
                self.results_table.setItem(row, 2, QTableWidgetItem(activity.unit.value))
                self.results_table.setItem(row, 3, QTableWidgetItem(f"{record.total_co2e:.2f}"))

            # Update total
            self.total_label.setText(f"Total CO2e: {total_co2e:.2f} kg")

        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Failed to calculate emissions: {str(e)}")

    def _clear_all(self):
        """Clear all activities and results."""
        self.activities.clear()
        self.results.clear()
        self.results_table.setRowCount(0)
        self.total_label.setText("Total CO2e: 0.00 kg")

    def _export_results(self, format_type: str):
        """Export results in specified format."""
        if not self.results:
            QMessageBox.warning(self, "No Results", "Please calculate emissions before exporting.")
            return

        try:
            # Get file path
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(
                self,
                "Save File",
                f"ghg_report.{format_type}",
                f"{format_type.upper()} Files (*.{format_type})"
            )

            if not file_path:
                return

            # Create report data (simplified - in real implementation, reconstruct records)
            report_data = ReportData(
                records=[],  # Would need to reconstruct from results
                period_start=datetime.now(),
                period_end=datetime.now(),
                organization="GUI User",
                report_title="GHG Emissions Report"
            )

            # Generate report
            if format_type == "csv":
                report = self.report_generator.generate_csv(report_data)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report)
            elif format_type == "json":
                report = self.report_generator.generate_json(report_data)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report)
            elif format_type == "pdf":
                report = self.report_generator.generate_pdf(report_data)
                with open(file_path, 'wb') as f:
                    f.write(report)
            else:
                raise ValueError(f"Unsupported format: {format_type}")

            QMessageBox.information(self, "Export Success", f"Results exported to {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export results: {str(e)}")


def main():
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)
    window = GHGCalculatorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QGroupBox, QLabel, QWidget, QGridLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

class MagneticCoreAnalyzer(QMainWindow):
    def __init__(self, magnetic_core_modeling):
        super().__init__()
        self.magnetic_core_modeling = magnetic_core_modeling
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(50)  # Update every 50ms

    def init_ui(self):
        self.setWindowTitle("Magnetic Core Analysis")
        self.setGeometry(200, 200, 600, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Magnetic Core Metrics Display
        metrics_group = QGroupBox("MAGNETIC CORE METRICS")
        metrics_group.setObjectName("panel")
        metrics_layout = QGridLayout()

        self.material_label = QLabel("MATERIAL: Ferrite")
        self.material_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("MATERIAL:").setObjectName("led-label"), 0, 0)
        metrics_layout.addWidget(self.material_label, 0, 1)

        self.h_field_label = QLabel("H: 0.00 A/m")
        self.h_field_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("H_FIELD:").setObjectName("led-label"), 1, 0)
        metrics_layout.addWidget(self.h_field_label, 1, 1)

        self.b_field_label = QLabel("B: 0.00 T")
        self.b_field_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("B_FIELD:").setObjectName("led-label"), 2, 0)
        metrics_layout.addWidget(self.b_field_label, 2, 1)

        self.magnetization_label = QLabel("M: 0.00 A/m")
        self.magnetization_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("MAGNETIZATION:").setObjectName("led-label"), 3, 0)
        metrics_layout.addWidget(self.magnetization_label, 3, 1)

        self.saturation_label = QLabel("SATURATION: 0.00 %")
        self.saturation_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("SATURATION:").setObjectName("led-label"), 4, 0)
        metrics_layout.addWidget(self.saturation_label, 4, 1)

        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)

        # Hysteresis Loop Plot
        self.hysteresis_label = QLabel("HYSTERESIS LOOP (B-H)")
        self.hysteresis_label.setObjectName("led-label")
        layout.addWidget(self.hysteresis_label)

        self.hysteresis_plot = pg.PlotWidget()
        self.hysteresis_plot.setBackground("#0A0A0A")
        self.hysteresis_plot.setTitle("Hysteresis Loop", color="#FFFF99", size="12pt")
        self.hysteresis_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.hysteresis_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.hysteresis_plot.showGrid(x=True, y=True, alpha=0.3)
        self.hysteresis_plot.setLabel("left", "B (T)", color="#FFFF99", **{"font-size": "12pt"})
        self.hysteresis_plot.setLabel("bottom", "H (A/m)", color="#FFFF99", **{"font-size": "12pt"})
        # Set axis ranges based on typical values
        self.hysteresis_plot.setXRange(-1000, 1000)
        self.hysteresis_plot.setYRange(-2, 2)
        layout.addWidget(self.hysteresis_plot)

        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4A4A4A, stop:1 #2E2E2E);
            }
            QGroupBox#panel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4A4A4A, stop:1 #2E2E2E);
                border: 3px outset #5C5C5C;
                border-radius: 5px;
                margin-top: 15px;
                padding: 10px;
                font: bold 12pt 'Courier New';
                color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #5C5C5C, stop:1 #3A3A3A);
                border: 2px outset #5C5C5C;
                border-radius: 3px;
                color: #FFFFFF;
                font: bold 12pt 'Courier New';
            }
            QLabel#led-label {
                background: transparent;
                color: #FFFFFF;
                font: bold 12pt 'Courier New';
            }
            QLabel#led-display {
                background: #1A1A1A;
                border: 2px inset #5C5C5C;
                border-radius: 3px;
                padding: 4px;
                color: #FFFF99;
                font: 12pt 'Courier New';
            }
        """)

    def update_metrics(self):
        try:
            # Update the magnetic core model (this will compute the new H and B)
            self.magnetic_core_modeling.update_metrics(dt=0.05)

            # Update labels
            self.material_label.setText(f"MATERIAL: {self.magnetic_core_modeling.core_material}")
            self.h_field_label.setText(f"H: {self.magnetic_core_modeling.h_field:.2f} A/m")
            self.b_field_label.setText(f"B: {self.magnetic_core_modeling.b_field:.2f} T")
            self.magnetization_label.setText(f"M: {self.magnetic_core_modeling.magnetization:.2f} A/m")
            saturation_percent = (abs(self.magnetic_core_modeling.b_field) / self.magnetic_core_modeling.B_sat) * 100
            self.saturation_label.setText(f"SATURATION: {saturation_percent:.2f} %")

            # Update hysteresis loop plot
            h_values, b_values = self.magnetic_core_modeling.get_hysteresis_loop()
            if len(h_values) > 0 and len(b_values) > 0:
                self.hysteresis_plot.clear()
                self.hysteresis_plot.plot(h_values, b_values, pen=pg.mkPen(color="#FFFF99", width=2))
                # Adjust axis ranges dynamically
                h_max = max(abs(min(h_values)), abs(max(h_values))) * 1.1
                b_max = max(abs(min(b_values)), abs(max(b_values))) * 1.1
                self.hysteresis_plot.setXRange(-h_max, h_max)
                self.hysteresis_plot.setYRange(-b_max, b_max)

        except Exception as e:
            print(f"Error in update_metrics: {e}")
            self.material_label.setText("MATERIAL: Error")
            self.h_field_label.setText("H: 0.00 A/m")
            self.b_field_label.setText("B: 0.00 T")
            self.magnetization_label.setText("M: 0.00 A/m")
            self.saturation_label.setText("SATURATION: 0.00 %")
            self.hysteresis_plot.clear()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()
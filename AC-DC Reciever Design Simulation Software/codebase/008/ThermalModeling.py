import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QGroupBox, QGridLayout,
    QSlider, QLineEdit, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QDoubleValidator, QFont

class ThermalAnalyzer(QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.model = model  # Reference to ReceiverModel
        self.time_data = np.linspace(0, 0.1, 1000)  # Match ReceiverModel's 0.1s waveform
        self.diode_power_data = np.zeros(1000)
        self.mosfet_power_data = np.zeros(1000)
        self.diode_temp_data = np.zeros(1000)
        self.mosfet_temp_data = np.zeros(1000)
        self.system_temp_data = np.zeros(1000)
        self.init_thermal_model()
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_thermal_analysis)
        self.timer.start(50)  # Update every 50ms to match MainWindow

    def init_thermal_model(self):
        # Thermal parameters (default values)
        self.ambient_temp = 25.0  # °C
        self.thermal_resistance_diode = 2.0  # °C/W
        self.thermal_resistance_mosfet = 1.5  # °C/W
        self.thermal_capacitance_diode = 0.1  # J/°C
        self.thermal_capacitance_mosfet = 0.08  # J/°C
        self.thermal_coupling = 0.2  # Thermal coupling factor between diode and MOSFET

        # Initialize temperatures
        self.diode_temp = self.ambient_temp
        self.mosfet_temp = self.ambient_temp
        self.system_temp = self.ambient_temp
        self.model.temperature = self.system_temp  # Update model for MainWindow

    def init_ui(self):
        self.setWindowTitle("Thermal Analysis")
        self.setGeometry(200, 200, 1000, 800)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Junction temperatures group
        metrics_group = QGroupBox("JUNCTION TEMPERATURES")
        metrics_group.setObjectName("panel")
        metrics_layout = QGridLayout()
        self.diode_temp_label = QLabel("DIODE: 25.00 °C")
        self.diode_temp_label.setObjectName("led-display")
        self.mosfet_temp_label = QLabel("MOSFET: 25.00 °C")
        self.mosfet_temp_label.setObjectName("led-display")
        self.system_temp_label = QLabel("SYSTEM: 25.00 °C")
        self.system_temp_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("DIODE:").setObjectName("led-label"), 0, 0)
        metrics_layout.addWidget(self.diode_temp_label, 0, 1)
        metrics_layout.addWidget(QLabel("MOSFET:").setObjectName("led-label"), 1, 0)
        metrics_layout.addWidget(self.mosfet_temp_label, 1, 1)
        metrics_layout.addWidget(QLabel("SYSTEM:").setObjectName("led-label"), 2, 0)
        metrics_layout.addWidget(self.system_temp_label, 2, 1)
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)

        # Thermal controls group
        controls_group = QGroupBox("THERMAL CONTROLS")
        controls_group.setObjectName("panel")
        controls_layout = QVBoxLayout()

        # Ambient temperature control
        ambient_layout = QHBoxLayout()
        ambient_label = QLabel("AMBIENT TEMP (°C):")
        ambient_label.setObjectName("led-label")
        self.ambient_input = QLineEdit("25.0")
        self.ambient_input.setValidator(QDoubleValidator(0.0, 50.0, 2))
        self.ambient_input.textChanged.connect(self.update_ambient_temp)
        ambient_layout.addWidget(ambient_label)
        ambient_layout.addWidget(self.ambient_input)
        controls_layout.addLayout(ambient_layout)

        # Diode thermal resistance control
        diode_rth_layout = QHBoxLayout()
        diode_rth_label = QLabel("DIODE Rth (°C/W):")
        diode_rth_label.setObjectName("led-label")
        self.diode_rth_input = QLineEdit("2.0")
        self.diode_rth_input.setValidator(QDoubleValidator(0.1, 10.0, 2))
        self.diode_rth_input.textChanged.connect(self.update_diode_rth)
        diode_rth_layout.addWidget(diode_rth_label)
        self.diode_rth_value = QLabel("2.00")
        self.diode_rth_value.setObjectName("led-display")
        self.diode_rth_slider = QSlider(Qt.Horizontal)
        self.diode_rth_slider.setRange(10, 1000)  # 0.1 to 10.0
        self.diode_rth_slider.setValue(200)  # 2.0
        self.diode_rth_slider.valueChanged.connect(self.update_diode_rth_slider)
        diode_rth_layout.addWidget(self.diode_rth_slider)
        diode_rth_layout.addWidget(self.diode_rth_input)
        diode_rth_layout.addWidget(self.diode_rth_value)
        controls_layout.addLayout(diode_rth_layout)

        # Diode thermal capacitance control
        diode_cth_layout = QHBoxLayout()
        diode_cth_label = QLabel("DIODE Cth (J/°C):")
        diode_cth_label.setObjectName("led-label")
        self.diode_cth_input = QLineEdit("0.1")
        self.diode_cth_input.setValidator(QDoubleValidator(0.01, 1.0, 3))
        self.diode_cth_input.textChanged.connect(self.update_diode_cth)
        diode_cth_layout.addWidget(diode_cth_label)
        self.diode_cth_value = QLabel("0.100")
        self.diode_cth_value.setObjectName("led-display")
        self.diode_cth_slider = QSlider(Qt.Horizontal)
        self.diode_cth_slider.setRange(1, 100)  # 0.01 to 1.0
        self.diode_cth_slider.setValue(10)  # 0.1
        self.diode_cth_slider.valueChanged.connect(self.update_diode_cth_slider)
        diode_cth_layout.addWidget(self.diode_cth_slider)
        diode_cth_layout.addWidget(self.diode_cth_input)
        diode_cth_layout.addWidget(self.diode_cth_value)
        controls_layout.addLayout(diode_cth_layout)

        # MOSFET thermal resistance control
        mosfet_rth_layout = QHBoxLayout()
        mosfet_rth_label = QLabel("MOSFET Rth (°C/W):")
        mosfet_rth_label.setObjectName("led-label")
        self.mosfet_rth_input = QLineEdit("1.5")
        self.mosfet_rth_input.setValidator(QDoubleValidator(0.1, 10.0, 2))
        self.mosfet_rth_input.textChanged.connect(self.update_mosfet_rth)
        mosfet_rth_layout.addWidget(mosfet_rth_label)
        self.mosfet_rth_value = QLabel("1.50")
        self.mosfet_rth_value.setObjectName("led-display")
        self.mosfet_rth_slider = QSlider(Qt.Horizontal)
        self.mosfet_rth_slider.setRange(10, 1000)  # 0.1 to 10.0
        self.mosfet_rth_slider.setValue(150)  # 1.5
        self.mosfet_rth_slider.valueChanged.connect(self.update_mosfet_rth_slider)
        mosfet_rth_layout.addWidget(self.mosfet_rth_slider)
        mosfet_rth_layout.addWidget(self.mosfet_rth_input)
        mosfet_rth_layout.addWidget(self.mosfet_rth_value)
        controls_layout.addLayout(mosfet_rth_layout)

        # MOSFET thermal capacitance control
        mosfet_cth_layout = QHBoxLayout()
        mosfet_cth_label = QLabel("MOSFET Cth (J/°C):")
        mosfet_cth_label.setObjectName("led-label")
        self.mosfet_cth_input = QLineEdit("0.08")
        self.mosfet_cth_input.setValidator(QDoubleValidator(0.01, 1.0, 3))
        self.mosfet_cth_input.textChanged.connect(self.update_mosfet_cth)
        mosfet_cth_layout.addWidget(mosfet_cth_label)
        self.mosfet_cth_value = QLabel("0.080")
        self.mosfet_cth_value.setObjectName("led-display")
        self.mosfet_cth_slider = QSlider(Qt.Horizontal)
        self.mosfet_cth_slider.setRange(1, 100)  # 0.01 to 1.0
        self.mosfet_cth_slider.setValue(8)  # 0.08
        self.mosfet_cth_slider.valueChanged.connect(self.update_mosfet_cth_slider)
        mosfet_cth_layout.addWidget(self.mosfet_cth_slider)
        mosfet_cth_layout.addWidget(self.mosfet_cth_input)
        mosfet_cth_layout.addWidget(self.mosfet_cth_value)
        controls_layout.addLayout(mosfet_cth_layout)

        # Reset button
        self.reset_button = QPushButton("RESET PARAMETERS")
        self.reset_button.clicked.connect(self.reset_parameters)
        controls_layout.addWidget(self.reset_button)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Power dissipation plot
        power_label = QLabel("POWER DISSIPATION (W)")
        power_label.setObjectName("led-label")
        layout.addWidget(power_label)
        self.power_plot = pg.PlotWidget()
        self.power_plot.setBackground("#0A0A0A")
        self.power_plot.setTitle("Power Dissipation vs Time", color="#FFFF99", size="12pt")
        self.power_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.power_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.power_plot.showGrid(x=True, y=True, alpha=0.3)
        self.power_plot.setXRange(0, 0.1)
        self.diode_power_curve = self.power_plot.plot(pen=pg.mkPen(color="#FF5555", width=2), name="Diode")
        self.mosfet_power_curve = self.power_plot.plot(pen=pg.mkPen(color="#55FF55", width=2), name="MOSFET")
        legend = self.power_plot.addLegend()
        legend.setBrush("#1A1A1A")
        legend.setPen({"color": "#FFFF99", "width": 2})
        # Remove invalid setTextPen call
        self.power_plot.setStyleSheet("""
            QGraphicsView {
                background: #0A0A0A;
            }
            QGraphicsTextItem {
                color: #FFFF99;
                font-family: 'Courier New';
                font-size: 12pt;
            }
        """)
        layout.addWidget(self.power_plot)

        # Temperature vs. time plot
        temp_label = QLabel("TEMPERATURE vs TIME (°C)")
        temp_label.setObjectName("led-label")
        layout.addWidget(temp_label)
        self.temp_plot = pg.PlotWidget()
        self.temp_plot.setBackground("#0A0A0A")
        self.temp_plot.setTitle("Temperature vs Time", color="#FFFF99", size="12pt")
        self.temp_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.temp_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.temp_plot.showGrid(x=True, y=True, alpha=0.3)
        self.temp_plot.setXRange(0, 0.1)
        self.diode_temp_curve = self.temp_plot.plot(pen=pg.mkPen(color="#FF5555", width=2), name="Diode")
        self.mosfet_temp_curve = self.temp_plot.plot(pen=pg.mkPen(color="#55FF55", width=2), name="MOSFET")
        self.system_temp_curve = self.temp_plot.plot(pen=pg.mkPen(color="#FFFF99", width=2), name="System")
        legend = self.temp_plot.addLegend()
        legend.setBrush("#1A1A1A")
        legend.setPen({"color": "#FFFF99", "width": 2})
        # Remove invalid setTextPen call
        self.temp_plot.setStyleSheet("""
            QGraphicsView {
                background: #0A0A0A;
            }
            QGraphicsTextItem {
                color: #FFFF99;
                font-family: 'Courier New';
                font-size: 12pt;
            }
        """)
        layout.addWidget(self.temp_plot)

        # Apply stylesheet for the main window
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
            QLineEdit {
                background: #1A1A1A;
                border: 2px inset #5C5C5C;
                border-radius: 3px;
                padding: 4px;
                color: #FFFF99;
                font: 12pt 'Courier New';
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #5C5C5C, stop:1 #3A3A3A);
                border: 3px outset #6C6C6C;
                border-radius: 5px;
                padding: 6px;
                color: #FFFFFF;
                font: bold 12pt 'Courier New';
                min-width: 150px;
                min-height: 30px;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3A3A3A, stop:1 #2E2E2E);
                border: 3px inset #6C6C6C;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #6C6C6C, stop:1 #4A4A4A);
            }
            QSlider {
                background: #1A1A1A;
                border: 2px inset #5C5C5C;
                border-radius: 3px;
                height: 20px;
            }
            QSlider::groove:horizontal {
                background: #2E2E2E;
                height: 8px;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #6C6C6C, stop:1 #4A4A4A);
                border: 2px outset #5C5C5C;
                width: 20px;
                margin: -8px 0;
                border-radius: 5px;
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

    def update_ambient_temp(self):
        try:
            self.ambient_temp = float(self.ambient_input.text())
        except ValueError:
            self.ambient_temp = 25.0
            self.ambient_input.setText("25.0")

    def update_diode_rth(self):
        try:
            self.thermal_resistance_diode = float(self.diode_rth_input.text())
            self.diode_rth_slider.setValue(int(self.thermal_resistance_diode * 100))
            self.diode_rth_value.setText(f"{self.thermal_resistance_diode:.2f}")
        except ValueError:
            self.thermal_resistance_diode = 2.0
            self.diode_rth_input.setText("2.0")
            self.diode_rth_slider.setValue(200)
            self.diode_rth_value.setText("2.00")

    def update_diode_rth_slider(self, value):
        self.thermal_resistance_diode = value / 100.0
        self.diode_rth_input.setText(f"{self.thermal_resistance_diode:.2f}")
        self.diode_rth_value.setText(f"{self.thermal_resistance_diode:.2f}")

    def update_diode_cth(self):
        try:
            self.thermal_capacitance_diode = float(self.diode_cth_input.text())
            self.diode_cth_slider.setValue(int(self.thermal_capacitance_diode * 100))
            self.diode_cth_value.setText(f"{self.thermal_capacitance_diode:.3f}")
        except ValueError:
            self.thermal_capacitance_diode = 0.1
            self.diode_cth_input.setText("0.1")
            self.diode_cth_slider.setValue(10)
            self.diode_cth_value.setText("0.100")

    def update_diode_cth_slider(self, value):
        self.thermal_capacitance_diode = value / 100.0
        self.diode_cth_input.setText(f"{self.thermal_capacitance_diode:.3f}")
        self.diode_cth_value.setText(f"{self.thermal_capacitance_diode:.3f}")

    def update_mosfet_rth(self):
        try:
            self.thermal_resistance_mosfet = float(self.mosfet_rth_input.text())
            self.mosfet_rth_slider.setValue(int(self.thermal_resistance_mosfet * 100))
            self.mosfet_rth_value.setText(f"{self.thermal_resistance_mosfet:.2f}")
        except ValueError:
            self.thermal_resistance_mosfet = 1.5
            self.mosfet_rth_input.setText("1.5")
            self.mosfet_rth_slider.setValue(150)
            self.mosfet_rth_value.setText("1.50")

    def update_mosfet_rth_slider(self, value):
        self.thermal_resistance_mosfet = value / 100.0
        self.mosfet_rth_input.setText(f"{self.thermal_resistance_mosfet:.2f}")
        self.mosfet_rth_value.setText(f"{self.thermal_resistance_mosfet:.2f}")

    def update_mosfet_cth(self):
        try:
            self.thermal_capacitance_mosfet = float(self.mosfet_cth_input.text())
            self.mosfet_cth_slider.setValue(int(self.thermal_capacitance_mosfet * 100))
            self.mosfet_cth_value.setText(f"{self.thermal_capacitance_mosfet:.3f}")
        except ValueError:
            self.thermal_capacitance_mosfet = 0.08
            self.mosfet_cth_input.setText("0.08")
            self.mosfet_cth_slider.setValue(8)
            self.mosfet_cth_value.setText("0.080")

    def update_mosfet_cth_slider(self, value):
        self.thermal_capacitance_mosfet = value / 100.0
        self.mosfet_cth_input.setText(f"{self.thermal_capacitance_mosfet:.3f}")
        self.mosfet_cth_value.setText(f"{self.thermal_capacitance_mosfet:.3f}")

    def reset_parameters(self):
        self.ambient_temp = 25.0
        self.ambient_input.setText("25.0")
        self.thermal_resistance_diode = 2.0
        self.diode_rth_input.setText("2.0")
        self.diode_rth_slider.setValue(200)
        self.diode_rth_value.setText("2.00")
        self.thermal_capacitance_diode = 0.1
        self.diode_cth_input.setText("0.1")
        self.diode_cth_slider.setValue(10)
        self.diode_cth_value.setText("0.100")
        self.thermal_resistance_mosfet = 1.5
        self.mosfet_rth_input.setText("1.5")
        self.mosfet_rth_slider.setValue(150)
        self.mosfet_rth_value.setText("1.50")
        self.thermal_capacitance_mosfet = 0.08
        self.mosfet_cth_input.setText("0.08")
        self.mosfet_cth_slider.setValue(8)
        self.mosfet_cth_value.setText("0.080")

    def update_thermal_analysis(self):
        if not self.model.power_on:
            # System is off, reset to ambient
            self.diode_temp = self.ambient_temp
            self.mosfet_temp = self.ambient_temp
            self.system_temp = self.ambient_temp
            self.diode_power_data = np.zeros(1000)
            self.mosfet_power_data = np.zeros(1000)
            self.diode_temp_data = np.full(1000, self.ambient_temp)
            self.mosfet_temp_data = np.full(1000, self.ambient_temp)
            self.system_temp_data = np.full(1000, self.ambient_temp)
        else:
            # Get waveforms from ReceiverModel
            t = self.time_data
            ac_signal, rectified_signal, modulated_signal = self.model.generate_waveform(t)

            # Simulate component currents and voltages
            # Diode: Assume it conducts during rectification, use rectified signal
            diode_voltage_drop = 0.7  # V (typical for a diode)
            diode_current = np.maximum(rectified_signal / 100.0, 0)  # Simplified current (A)
            self.diode_power_data = diode_current * diode_voltage_drop  # Power dissipation (W)

            # MOSFET: Assume it switches in the regulator, use modulated signal
            mosfet_rds_on = 0.1  # Ω (on-resistance)
            mosfet_current = np.abs(modulated_signal / 50.0)  # Simplified current (A)
            self.mosfet_power_data = mosfet_current**2 * mosfet_rds_on  # Power dissipation (W)

            # Update temperatures using RC thermal model
            delta_t = 0.05  # Update interval (50ms)
            for i in range(len(t)):
                # Diode temperature
                power_diode = self.diode_power_data[i]
                coupling_heat = self.thermal_coupling * (self.mosfet_temp - self.diode_temp)
                delta_temp_diode = (power_diode * self.thermal_resistance_diode +
                                  coupling_heat -
                                  (self.diode_temp - self.ambient_temp)) * delta_t / self.thermal_capacitance_diode
                self.diode_temp += delta_temp_diode
                self.diode_temp_data[i] = self.diode_temp

                # MOSFET temperature
                power_mosfet = self.mosfet_power_data[i]
                coupling_heat = self.thermal_coupling * (self.diode_temp - self.mosfet_temp)
                delta_temp_mosfet = (power_mosfet * self.thermal_resistance_mosfet +
                                   coupling_heat -
                                   (self.mosfet_temp - self.ambient_temp)) * delta_t / self.thermal_capacitance_mosfet
                self.mosfet_temp += delta_temp_mosfet
                self.mosfet_temp_data[i] = self.mosfet_temp

                # System temperature (average)
                self.system_temp = (self.diode_temp + self.mosfet_temp) / 2.0
                self.system_temp_data[i] = self.system_temp

        # Update model temperature for MainWindow
        self.model.temperature = self.system_temp

        # Update labels
        self.diode_temp_label.setText(f"DIODE: {self.diode_temp:.2f} °C")
        self.mosfet_temp_label.setText(f"MOSFET: {self.mosfet_temp:.2f} °C")
        self.system_temp_label.setText(f"SYSTEM: {self.system_temp:.2f} °C")

        # Update plots
        self.diode_power_curve.setData(self.time_data, self.diode_power_data)
        self.mosfet_power_curve.setData(self.time_data, self.mosfet_power_data)
        self.diode_temp_curve.setData(self.time_data, self.diode_temp_data)
        self.mosfet_temp_curve.setData(self.time_data, self.mosfet_temp_data)
        self.system_temp_curve.setData(self.time_data, self.system_temp_data)

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()
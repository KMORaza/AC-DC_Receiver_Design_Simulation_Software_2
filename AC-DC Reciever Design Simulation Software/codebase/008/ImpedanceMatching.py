import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QGroupBox
from PyQt5.QtCore import Qt

class ImpedanceMatchingAnalyzer:
    def __init__(self, model):
        self.model = model
        self.z_source = 50 + 0j
        self.z_load = 50 + 0j
        self.z_in = 50 + 0j
        self.z_out = 50 + 0j
        self.gamma_in = 0.0
        self.gamma_out = 0.0
        self.return_loss_in = 0.0
        self.return_loss_out = 0.0
        self.vswr_in = 1.0
        self.vswr_out = 1.0
        self.init_ui()

    def init_ui(self):
        self.widget = QWidget()
        layout = QVBoxLayout()

        # Set global stylesheet for white foreground color
        self.widget.setStyleSheet("""
            QLabel#led-display, QLabel#led-label {
                color: white;
            }
            QGroupBox::title {
                color: white;
            }
        """)

        # Impedance Metrics Group
        impedance_group = QGroupBox("IMPEDANCE METRICS")
        impedance_layout = QGridLayout()

        # Labels for displaying values
        self.z_in_label = QLabel("Z_IN: 50.00 + j0.00 Ω")
        self.z_in_label.setObjectName("led-display")
        self.z_out_label = QLabel("Z_OUT: 50.00 + j0.00 Ω")
        self.z_out_label.setObjectName("led-display")
        self.gamma_in_label = QLabel("GAMMA_IN: 0.00")
        self.gamma_in_label.setObjectName("led-display")
        self.gamma_out_label = QLabel("GAMMA_OUT: 0.00")
        self.gamma_out_label.setObjectName("led-display")
        self.return_loss_in_label = QLabel("RL_IN: 0.00 dB")
        self.return_loss_in_label.setObjectName("led-display")
        self.return_loss_out_label = QLabel("RL_OUT: 0.00 dB")
        self.return_loss_out_label.setObjectName("led-display")
        self.vswr_in_label = QLabel("VSWR_IN: 1.00")
        self.vswr_in_label.setObjectName("led-display")
        self.vswr_out_label = QLabel("VSWR_OUT: 1.00")
        self.vswr_out_label.setObjectName("led-display")

        # Add rows of labels
        rows = [
            ("Z_IN:", self.z_in_label),
            ("Z_OUT:", self.z_out_label),
            ("GAMMA_IN:", self.gamma_in_label),
            ("GAMMA_OUT:", self.gamma_out_label),
            ("RL_IN:", self.return_loss_in_label),
            ("RL_OUT:", self.return_loss_out_label),
            ("VSWR_IN:", self.vswr_in_label),
            ("VSWR_OUT:", self.vswr_out_label)
        ]

        for i, (name, value_label) in enumerate(rows):
            name_label = QLabel(name)
            name_label.setObjectName("led-label")
            impedance_layout.addWidget(name_label, i, 0)
            impedance_layout.addWidget(value_label, i, 1)

        impedance_group.setLayout(impedance_layout)
        layout.addWidget(impedance_group)
        self.widget.setLayout(layout)

    def set_source_impedance(self, r, x):
        try:
            self.z_source = complex(r, x)
            self.update_impedance_metrics()
        except ValueError:
            pass

    def set_load_impedance(self, r, x):
        try:
            self.z_load = complex(r, x)
            self.update_impedance_metrics()
        except ValueError:
            pass

    def update_impedance_metrics(self):
        if not self.model.power_on:
            self.z_in = 50 + 0j
            self.z_out = 50 + 0j
            self.gamma_in = 0.0
            self.gamma_out = 0.0
            self.return_loss_in = 0.0
            self.return_loss_out = 0.0
            self.vswr_in = 1.0
            self.vswr_out = 1.0
        else:
            freq = self.model.frequency
            c = self.model.filter_capacitance
            l = self.model.filter_inductance
            r_rect = 10.0
            r_reg = 5.0

            z_c = 1 / (2 * np.pi * freq * c * 1j) if c > 0 else 1e6
            z_l = 2 * np.pi * freq * l * 1j if l > 0 else 0
            self.z_in = r_rect + z_c + z_l
            self.z_out = r_reg

            self.gamma_in = (self.z_in - self.z_source) / (self.z_in + self.z_source)
            self.gamma_out = (self.z_load - self.z_out) / (self.z_load + self.z_out)

            self.return_loss_in = -20 * np.log10(np.abs(self.gamma_in)) if np.abs(self.gamma_in) > 0 else 100
            self.return_loss_out = -20 * np.log10(np.abs(self.gamma_out)) if np.abs(self.gamma_out) > 0 else 100

            self.vswr_in = (1 + np.abs(self.gamma_in)) / (1 - np.abs(self.gamma_in)) if np.abs(self.gamma_in) < 1 else 100
            self.vswr_out = (1 + np.abs(self.gamma_out)) / (1 - np.abs(self.gamma_out)) if np.abs(self.gamma_out) < 1 else 100

        # Update display
        self.z_in_label.setText(f"Z_IN: {self.z_in.real:.2f} + j{self.z_in.imag:.2f} Ω")
        self.z_out_label.setText(f"Z_OUT: {self.z_out.real:.2f} + j{self.z_out.imag:.2f} Ω")
        self.gamma_in_label.setText(f"GAMMA_IN: {np.abs(self.gamma_in):.2f}")
        self.gamma_out_label.setText(f"GAMMA_OUT: {np.abs(self.gamma_out):.2f}")
        self.return_loss_in_label.setText(f"RL_IN: {self.return_loss_in:.2f} dB")
        self.return_loss_out_label.setText(f"RL_OUT: {self.return_loss_out:.2f} dB")
        self.vswr_in_label.setText(f"VSWR_IN: {self.vswr_in:.2f}")
        self.vswr_out_label.setText(f"VSWR_OUT: {self.vswr_out:.2f}")

    def get_smith_chart_data(self):
        z0 = 50.0
        z_in_norm = self.z_in / z0
        z_out_norm = self.z_out / z0

        gamma_in = (z_in_norm - 1) / (z_in_norm + 1)
        gamma_out = (z_out_norm - 1) / (z_out_norm + 1)

        return {
            'gamma_in': (gamma_in.real, gamma_in.imag),
            'gamma_out': (gamma_out.real, gamma_out.imag)
        }

    def get_gamma_vs_freq(self):
        if not self.model.power_on:
            return np.array([100, 10000]), np.array([0, 0])

        freqs = np.logspace(2, 4, 100)
        gamma_in_vals = []
        c = self.model.filter_capacitance
        l = self.model.filter_inductance
        r_rect = 10.0

        for f in freqs:
            z_c = 1 / (2 * np.pi * f * c * 1j) if c > 0 else 1e6
            z_l = 2 * np.pi * f * l * 1j if l > 0 else 0
            z_in = r_rect + z_c + z_l
            gamma = np.abs((z_in - self.z_source) / (z_in + self.z_source))
            gamma_in_vals.append(gamma)

        return freqs, np.array(gamma_in_vals)

    def get_widget(self):
        return self.widget

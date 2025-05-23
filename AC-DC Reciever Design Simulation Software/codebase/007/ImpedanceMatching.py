import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QGroupBox
from PyQt5.QtCore import Qt

class ImpedanceMatchingAnalyzer:
    def __init__(self, model):
        self.model = model
        self.z_source = 50 + 0j  # Default: 50 + j0 Ω
        self.z_load = 50 + 0j    # Default: 50 + j0 Ω
        self.z_in = 50 + 0j      # Placeholder
        self.z_out = 50 + 0j     # Placeholder
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

        # Impedance Metrics
        impedance_group = QGroupBox("IMPEDANCE METRICS")
        impedance_group.setObjectName("panel")
        impedance_layout = QGridLayout()
        
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

        impedance_layout.addWidget(QLabel("Z_IN:").setObjectName("led-label"), 0, 0)
        impedance_layout.addWidget(self.z_in_label, 0, 1)
        impedance_layout.addWidget(QLabel("Z_OUT:").setObjectName("led-label"), 1, 0)
        impedance_layout.addWidget(self.z_out_label, 1, 1)
        impedance_layout.addWidget(QLabel("GAMMA_IN:").setObjectName("led-label"), 2, 0)
        impedance_layout.addWidget(self.gamma_in_label, 2, 1)
        impedance_layout.addWidget(QLabel("GAMMA_OUT:").setObjectName("led-label"), 3, 0)
        impedance_layout.addWidget(self.gamma_out_label, 3, 1)
        impedance_layout.addWidget(QLabel("RL_IN:").setObjectName("led-label"), 4, 0)
        impedance_layout.addWidget(self.return_loss_in_label, 4, 1)
        impedance_layout.addWidget(QLabel("RL_OUT:").setObjectName("led-label"), 5, 0)
        impedance_layout.addWidget(self.return_loss_out_label, 5, 1)
        impedance_layout.addWidget(QLabel("VSWR_IN:").setObjectName("led-label"), 6, 0)
        impedance_layout.addWidget(self.vswr_in_label, 6, 1)
        impedance_layout.addWidget(QLabel("VSWR_OUT:").setObjectName("led-label"), 7, 0)
        impedance_layout.addWidget(self.vswr_out_label, 7, 1)

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
            # Simplified impedance model
            freq = self.model.frequency
            c = self.model.filter_capacitance
            l = self.model.filter_inductance
            r_rect = 10.0  # Approximate rectifier resistance
            r_reg = 5.0    # Approximate regulator resistance

            # Input impedance: rectifier + filter
            z_c = 1 / (2 * np.pi * freq * c * 1j) if c > 0 else 1e6
            z_l = 2 * np.pi * freq * l * 1j if l > 0 else 0
            self.z_in = r_rect + z_c + z_l

            # Output impedance: regulator + load effect
            self.z_out = r_reg  # Simplified; assumes regulator dominates

            # Reflection coefficients
            self.gamma_in = (self.z_in - self.z_source) / (self.z_in + self.z_source)
            self.gamma_out = (self.z_load - self.z_out) / (self.z_load + self.z_out)

            # Return loss
            self.return_loss_in = -20 * np.log10(np.abs(self.gamma_in)) if np.abs(self.gamma_in) > 0 else 100
            self.return_loss_out = -20 * np.log10(np.abs(self.gamma_out)) if np.abs(self.gamma_out) > 0 else 100

            # VSWR
            self.vswr_in = (1 + np.abs(self.gamma_in)) / (1 - np.abs(self.gamma_in)) if np.abs(self.gamma_in) < 1 else 100
            self.vswr_out = (1 + np.abs(self.gamma_out)) / (1 - np.abs(self.gamma_out)) if np.abs(self.gamma_out) < 1 else 100

        # Update labels
        self.z_in_label.setText(f"Z_IN: {self.z_in.real:.2f} + j{self.z_in.imag:.2f} Ω")
        self.z_out_label.setText(f"Z_OUT: {self.z_out.real:.2f} + j{self.z_out.imag:.2f} Ω")
        self.gamma_in_label.setText(f"GAMMA_IN: {np.abs(self.gamma_in):.2f}")
        self.gamma_out_label.setText(f"GAMMA_OUT: {np.abs(self.gamma_out):.2f}")
        self.return_loss_in_label.setText(f"RL_IN: {self.return_loss_in:.2f} dB")
        self.return_loss_out_label.setText(f"RL_OUT: {self.return_loss_out:.2f} dB")
        self.vswr_in_label.setText(f"VSWR_IN: {self.vswr_in:.2f}")
        self.vswr_out_label.setText(f"VSWR_OUT: {self.vswr_out:.2f}")

    def get_smith_chart_data(self):
        # Normalize impedances
        z0 = 50.0  # Reference impedance
        z_in_norm = self.z_in / z0
        z_out_norm = self.z_out / z0

        # Convert to reflection coefficients for Smith Chart
        gamma_in = (z_in_norm - 1) / (z_in_norm + 1)
        gamma_out = (z_out_norm - 1) / (z_out_norm + 1)

        # Generate points for plotting (real, imag)
        return {
            'gamma_in': (gamma_in.real, gamma_in.imag),
            'gamma_out': (gamma_out.real, gamma_out.imag)
        }

    def get_gamma_vs_freq(self):
        if not self.model.power_on:
            return np.array([100, 10000]), np.array([0, 0])

        freqs = np.logspace(2, 4, 100)  # 100 Hz to 10 kHz
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
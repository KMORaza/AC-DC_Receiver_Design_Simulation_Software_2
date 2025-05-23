import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QGridLayout
from PyQt5.QtGui import QFont

class ImpedanceMatchingAnalyzer:
    def __init__(self, model):
        self.model = model
        self.r_source = 50.0
        self.x_source = 0.0
        self.r_load = 50.0
        self.x_load = 0.0
        self.Z0 = 50.0  # Characteristic impedance for normalization
        self.frequencies = np.logspace(2, 5, 100)  # 100 Hz to 100 kHz
        self.widget = QWidget()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Stability Metrics Display
        self.metrics_group = QGroupBox("IMPEDANCE METRICS")
        self.metrics_group.setObjectName("panel")
        metrics_layout = QGridLayout()

        self.z_source_label = QLabel("Z_SRC: 50.00 + j0.00 Ω")
        self.z_source_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("Z_SRC:").setObjectName("led-label"), 0, 0)
        metrics_layout.addWidget(self.z_source_label, 0, 1)

        self.z_load_label = QLabel("Z_LOAD: 50.00 + j0.00 Ω")
        self.z_load_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("Z_LOAD:").setObjectName("led-label"), 1, 0)
        metrics_layout.addWidget(self.z_load_label, 1, 1)

        self.gamma_label = QLabel("GAMMA: 0.00")
        self.gamma_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("GAMMA:").setObjectName("led-label"), 2, 0)
        metrics_layout.addWidget(self.gamma_label, 2, 1)

        # Add new metrics
        self.z_in_label = QLabel("Z_IN: 50.00 + j0.00 Ω")
        self.z_in_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("Z_IN:").setObjectName("led-label"), 3, 0)
        metrics_layout.addWidget(self.z_in_label, 3, 1)

        self.z_out_label = QLabel("Z_OUT: 50.00 + j0.00 Ω")
        self.z_out_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("Z_OUT:").setObjectName("led-label"), 4, 0)
        metrics_layout.addWidget(self.z_out_label, 4, 1)

        self.vswr_label = QLabel("VSWR: 1.00")
        self.vswr_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("VSWR:").setObjectName("led-label"), 5, 0)
        metrics_layout.addWidget(self.vswr_label, 5, 1)

        self.return_loss_label = QLabel("RL: 0.00 dB")
        self.return_loss_label.setObjectName("led-display")
        metrics_layout.addWidget(QLabel("RL:").setObjectName("led-label"), 6, 0)
        metrics_layout.addWidget(self.return_loss_label, 6, 1)

        self.metrics_group.setLayout(metrics_layout)
        layout.addWidget(self.metrics_group)

        self.widget.setLayout(layout)

        # Apply stylesheet
        self.widget.setStyleSheet("""
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

    def get_widget(self):
        return self.widget

    def set_source_impedance(self, r, x):
        print(f"ImpedanceMatchingAnalyzer: Setting source impedance - r={r}, x={x}")
        self.r_source = r
        self.x_source = x
        self.update_impedance_metrics()

    def set_load_impedance(self, r, x):
        print(f"ImpedanceMatchingAnalyzer: Setting load impedance - r={r}, x={x}")
        self.r_load = r
        self.x_load = x
        self.update_impedance_metrics()

    def update_impedance_metrics(self):
        try:
            # Source and Load Impedance
            z_source = complex(self.r_source, self.x_source)
            z_load = complex(self.r_load, self.x_load)

            # Normalize impedances
            gamma = (z_load - self.Z0) / (z_load + self.Z0)  # Reflection coefficient at load
            gamma_mag = np.abs(gamma)

            # Compute additional metrics
            # Input Impedance (simplified, assuming direct connection for now)
            z_in = z_load  # In a simple circuit, Z_in = Z_load; in a real network, this would involve S-parameters or ABCD matrix
            z_out = z_source  # Similarly, Z_out = Z_source for this simplified model

            # VSWR
            vswr = (1 + gamma_mag) / (1 - gamma_mag + 1e-10)  # Avoid division by zero

            # Return Loss (in dB)
            return_loss = -20 * np.log10(gamma_mag + 1e-10)  # Avoid log(0)

            # Update labels in the main metrics display
            self.z_source_label.setText(f"Z_SRC: {self.r_source:.2f} + j{self.x_source:.2f} Ω")
            self.z_load_label.setText(f"Z_LOAD: {self.r_load:.2f} + j{self.x_load:.2f} Ω")
            self.gamma_label.setText(f"GAMMA: {gamma_mag:.2f}")
            self.z_in_label.setText(f"Z_IN: {z_in.real:.2f} + j{z_in.imag:.2f} Ω")
            self.z_out_label.setText(f"Z_OUT: {z_out.real:.2f} + j{z_out.imag:.2f} Ω")
            self.vswr_label.setText(f"VSWR: {vswr:.2f}")
            self.return_loss_label.setText(f"RL: {return_loss:.2f} dB")

        except Exception as e:
            print(f"Error in update_impedance_metrics: {e}")
            # Set default values to prevent UI crashes
            self.z_source_label.setText("Z_SRC: 0.00 + j0.00 Ω")
            self.z_load_label.setText("Z_LOAD: 0.00 + j0.00 Ω")
            self.gamma_label.setText("GAMMA: 0.00")
            self.z_in_label.setText("Z_IN: 0.00 + j0.00 Ω")
            self.z_out_label.setText("Z_OUT: 0.00 + j0.00 Ω")
            self.vswr_label.setText("VSWR: 1.00")
            self.return_loss_label.setText("RL: 0.00 dB")

    def get_smith_chart_data(self):
        z_load = complex(self.r_load, self.x_load)
        gamma = (z_load - self.Z0) / (z_load + self.Z0)
        z_source = complex(self.r_source, self.x_source)
        gamma_source = (z_source - self.Z0) / (z_source + self.Z0)
        return {
            'gamma_in': (gamma.real, gamma.imag),
            'gamma_out': (gamma_source.real, gamma_source.imag)
        }

    def get_gamma_vs_freq(self):
        gamma_mags = []
        for freq in self.frequencies:
            # Simplified: Assume load impedance is frequency-independent for now
            z_load = complex(self.r_load, self.x_load)
            gamma = (z_load - self.Z0) / (z_load + self.Z0)
            gamma_mags.append(np.abs(gamma))
        return self.frequencies, gamma_mags
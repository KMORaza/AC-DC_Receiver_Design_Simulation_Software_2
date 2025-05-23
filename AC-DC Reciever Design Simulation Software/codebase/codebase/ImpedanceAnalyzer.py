import sys
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QGroupBox, QLabel, QWidget, QGridLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

class ImpedanceAnalyzer(QMainWindow):
    def __init__(self, impedance_analyzer):
        super().__init__()
        self.impedance_analyzer = impedance_analyzer
        self.Z0 = 50.0  # Characteristic impedance for normalization, matching ImpedanceMatchingAnalyzer
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(50)  # Update every 50ms, matching MainWindow's update rate

    def init_ui(self):
        self.setWindowTitle("Impedance Analysis")
        self.setGeometry(200, 200, 400, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Impedance Metrics Display
        metrics_group = QGroupBox("IMPEDANCE METRICS")
        metrics_group.setObjectName("panel")
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

        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)

        layout.addStretch()

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
            # Directly access the impedance values from ImpedanceMatchingAnalyzer
            r_source = self.impedance_analyzer.r_source
            x_source = self.impedance_analyzer.x_source
            r_load = self.impedance_analyzer.r_load
            x_load = self.impedance_analyzer.x_load

            # Debug print to confirm values are being accessed
            print(f"ImpedanceAnalyzer: r_source={r_source}, x_source={x_source}, r_load={r_load}, x_load={x_load}")

            # Source and Load Impedance
            z_source = complex(r_source, x_source)
            z_load = complex(r_load, x_load)

            # Normalize impedances
            gamma = (z_load - self.Z0) / (z_load + self.Z0)  # Reflection coefficient at load
            gamma_mag = np.abs(gamma)

            # Compute additional metrics
            z_in = z_load  # Simplified, as in ImpedanceMatchingAnalyzer
            z_out = z_source  # Simplified, as in ImpedanceMatchingAnalyzer

            # VSWR
            vswr = (1 + gamma_mag) / (1 - gamma_mag + 1e-10)  # Avoid division by zero

            # Return Loss (in dB)
            return_loss = -20 * np.log10(gamma_mag + 1e-10)  # Avoid log(0)

            # Update the labels
            self.z_source_label.setText(f"Z_SRC: {r_source:.2f} + j{x_source:.2f} Ω")
            self.z_load_label.setText(f"Z_LOAD: {r_load:.2f} + j{x_load:.2f} Ω")
            self.gamma_label.setText(f"GAMMA: {gamma_mag:.2f}")
            self.z_in_label.setText(f"Z_IN: {z_in.real:.2f} + j{z_in.imag:.2f} Ω")
            self.z_out_label.setText(f"Z_OUT: {z_out.real:.2f} + j{z_out.imag:.2f} Ω")
            self.vswr_label.setText(f"VSWR: {vswr:.2f}")
            self.return_loss_label.setText(f"RL: {return_loss:.2f} dB")

        except Exception as e:
            print(f"Error in ImpedanceAnalyzer update_metrics: {e}")
            # Set default values to prevent UI crashes
            self.z_source_label.setText("Z_SRC: 0.00 + j0.00 Ω")
            self.z_load_label.setText("Z_LOAD: 0.00 + j0.00 Ω")
            self.gamma_label.setText("GAMMA: 0.00")
            self.z_in_label.setText("Z_IN: 0.00 + j0.00 Ω")
            self.z_out_label.setText("Z_OUT: 0.00 + j0.00 Ω")
            self.vswr_label.setText("VSWR: 1.00")
            self.return_loss_label.setText("RL: 0.00 dB")

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)
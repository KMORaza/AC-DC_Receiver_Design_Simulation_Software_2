import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QGridLayout
from PyQt5.QtGui import QFont

class MagneticCoreModeling:
    def __init__(self, model):
        self.model = model
        self.core_material = "Ferrite"  # Default material
        self.h_field_base = 100.0  # Base magnetic field intensity (A/m) set by user
        self.h_field = 0.0  # Current magnetic field intensity (A/m), will vary with simulation
        self.b_field = 0.0  # Magnetic flux density (T)
        self.magnetization = 0.0  # Magnetization (A/m)
        self.time = 0.0  # Simulation time
        self.h_history = []  # History of H values for hysteresis loop
        self.b_history = []  # History of B values for hysteresis loop
        self.max_history = 200  # Number of points to store for the hysteresis loop
        self.widget = QWidget()
        self.init_ui()
        self.update_core_properties()

    def init_ui(self):
        layout = QVBoxLayout()

        # Magnetic Core Metrics Display
        self.metrics_group = QGroupBox("MAGNETIC CORE METRICS")
        self.metrics_group.setObjectName("panel")
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

    def set_core_material(self, material):
        self.core_material = material
        self.update_core_properties()
        self.update_metrics()

    def set_magnetic_field(self, h_field_base):
        self.h_field_base = h_field_base
        self.update_metrics()

    def update_core_properties(self):
        # Material properties (simplified for demonstration)
        # B_sat: Saturation flux density (T)
        # mu_r: Relative permeability
        # H_c: Coercivity (A/m)
        # M_s: Saturation magnetization (A/m)
        self.material_properties = {
            "Ferrite": {"B_sat": 0.4, "mu_r": 2000, "H_c": 20, "M_s": 3e5},
            "Iron Powder": {"B_sat": 1.0, "mu_r": 100, "H_c": 50, "M_s": 8e5},
            "Silicon Steel": {"B_sat": 1.5, "mu_r": 4000, "H_c": 10, "M_s": 1.2e6}
        }
        self.B_sat = self.material_properties[self.core_material]["B_sat"]
        self.mu_r = self.material_properties[self.core_material]["mu_r"]
        self.H_c = self.material_properties[self.core_material]["H_c"]
        self.M_s = self.material_properties[self.core_material]["M_s"]
        self.mu_0 = 4 * np.pi * 1e-7  # Permeability of free space (H/m)

    def update_metrics(self, dt=0.05):
        try:
            # Increment simulation time
            self.time += dt

            # Get the frequency from the model (in Hz)
            freq = self.model.frequency

            # Compute a time-varying H field: H(t) = H_base * sin(2πft)
            self.h_field = self.h_field_base * np.sin(2 * np.pi * freq * self.time)

            # Simplified Jiles-Atherton model for hysteresis
            # Parameters for Jiles-Atherton model
            a = self.H_c / 2  # Domain wall pinning constant
            alpha = 1e-3  # Inter-domain coupling
            k = self.H_c  # Domain wall pinning constant
            c = 0.1  # Reversible magnetization coefficient

            # Effective field
            H_eff = self.h_field + alpha * self.magnetization

            # Anhysteretic magnetization (Langevin function approximation)
            # Avoid division by zero in the Langevin function
            if abs(H_eff / a) < 1e-6:
                M_an = self.M_s * (H_eff / (3 * a))
            else:
                M_an = self.M_s * (1 / np.tanh(H_eff / a) - a / H_eff)

            # Differential equation for magnetization (simplified)
            delta_M = M_an - self.magnetization
            if abs(k - alpha * delta_M) < 1e-6:
                dM_dH = 0
            else:
                dM_dH = delta_M / (k - alpha * delta_M)
            delta = 1 if self.h_field > 0 else -1
            dM_dH = dM_dH * (1 - c) + c * delta_M / a
            self.magnetization += dM_dH * delta

            # Limit magnetization to saturation
            self.magnetization = max(-self.M_s, min(self.M_s, self.magnetization))

            # Magnetic flux density B = mu_0 * (H + M)
            self.b_field = self.mu_0 * (self.h_field + self.magnetization)

            # Limit B to saturation
            self.b_field = max(-self.B_sat, min(self.B_sat, self.b_field))

            # Calculate saturation percentage
            saturation_percent = (abs(self.b_field) / self.B_sat) * 100

            # Update history for hysteresis loop
            self.h_history.append(self.h_field)
            self.b_history.append(self.b_field)
            if len(self.h_history) > self.max_history:
                self.h_history.pop(0)
                self.b_history.pop(0)

            # Update labels
            self.material_label.setText(f"MATERIAL: {self.core_material}")
            self.h_field_label.setText(f"H: {self.h_field:.2f} A/m")
            self.b_field_label.setText(f"B: {self.b_field:.2f} T")
            self.magnetization_label.setText(f"M: {self.magnetization:.2f} A/m")
            self.saturation_label.setText(f"SATURATION: {saturation_percent:.2f} %")

        except Exception as e:
            print(f"Error in update_metrics: {e}")
            self.material_label.setText(f"MATERIAL: {self.core_material}")
            self.h_field_label.setText("H: 0.00 A/m")
            self.b_field_label.setText("B: 0.00 T")
            self.magnetization_label.setText("M: 0.00 A/m")
            self.saturation_label.setText("SATURATION: 0.00 %")

    def get_hysteresis_loop(self):
        # Return the history of H and B values for plotting
        return np.array(self.h_history), np.array(self.b_history)
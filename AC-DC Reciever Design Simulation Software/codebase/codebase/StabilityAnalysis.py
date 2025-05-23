import numpy as np
from scipy import signal
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
import control
from control import TransferFunction as ControlTF

class StabilityAnalyzer:
    def __init__(self, model):
        self.model = model
        self.init_ui()

    def init_ui(self):
        """Initialize plot widgets for stability analysis."""
        self.widget = QWidget()
        layout = QVBoxLayout()

        # Bode Plot
        self.bode_label = QLabel("BODE PLOT")
        self.bode_label.setObjectName("led-label")
        layout.addWidget(self.bode_label)
        self.bode_plot = pg.PlotWidget()
        self.bode_plot.setBackground("#0A0A0A")
        self.bode_plot.setTitle("Bode Plot", color="#FFFF99", size="12pt")
        self.bode_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.bode_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.bode_plot.showGrid(x=True, y=True, alpha=0.3)
        self.bode_plot.setLogMode(x=True, y=False)
        self.bode_plot.setLabel("left", "Magnitude (dB)", color="#FFFF99")
        self.bode_plot.setLabel("bottom", "Frequency (Hz)", color="#FFFF99")
        layout.addWidget(self.bode_plot)

        # Phase Plot (part of Bode)
        self.phase_label = QLabel("PHASE PLOT")
        self.phase_label.setObjectName("led-label")
        layout.addWidget(self.phase_label)
        self.phase_plot = pg.PlotWidget()
        self.phase_plot.setBackground("#0A0A0A")
        self.phase_plot.setTitle("Phase Plot", color="#FFFF99", size="12pt")
        self.phase_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.phase_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.phase_plot.showGrid(x=True, y=True, alpha=0.3)
        self.phase_plot.setLogMode(x=True, y=False)
        self.phase_plot.setLabel("left", "Phase (degrees)", color="#FFFF99")
        self.phase_plot.setLabel("bottom", "Frequency (Hz)", color="#FFFF99")
        layout.addWidget(self.phase_plot)

        # Nyquist Plot
        self.nyquist_label = QLabel("NYQUIST PLOT")
        self.nyquist_label.setObjectName("led-label")
        layout.addWidget(self.nyquist_label)
        self.nyquist_plot = pg.PlotWidget()
        self.nyquist_plot.setBackground("#0A0A0A")
        self.nyquist_plot.setTitle("Nyquist Plot", color="#FFFF99", size="12pt")
        self.nyquist_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.nyquist_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.nyquist_plot.showGrid(x=True, y=True, alpha=0.3)
        self.nyquist_plot.setLabel("left", "Imaginary", color="#FFFF99")
        self.nyquist_plot.setLabel("bottom", "Real", color="#FFFF99")
        layout.addWidget(self.nyquist_plot)

        # Root Locus Plot
        self.root_locus_label = QLabel("ROOT LOCUS")
        self.root_locus_label.setObjectName("led-label")
        layout.addWidget(self.root_locus_label)
        self.root_locus_plot = pg.PlotWidget()
        self.root_locus_plot.setBackground("#0A0A0A")
        self.root_locus_plot.setTitle("Root Locus", color="#FFFF99", size="12pt")
        self.root_locus_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.root_locus_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.root_locus_plot.showGrid(x=True, y=True, alpha=0.3)
        self.root_locus_plot.setLabel("left", "Imaginary", color="#FFFF99")
        self.root_locus_plot.setLabel("bottom", "Real", color="#FFFF99")
        layout.addWidget(self.root_locus_plot)

        self.widget.setLayout(layout)

    def get_system(self):
        """Return the transfer function of the system based on filter and regulator."""
        # Ensure non-zero and stable parameters
        R = max(self.model.load_resistance + self.model.parasitic_resistance, 1e-6)
        C = max(self.model.filter_capacitance, 1e-9)
        L = max(self.model.filter_inductance, 1e-6)
        cutoff = max(self.model.active_filter_cutoff, 1.0)
        opamp_gain = min(self.model.opamp_gain, 1e6)  # Cap opamp gain to avoid instability

        if self.model.filter_type == "capacitive":
            # RC low-pass filter
            num = [1]
            den = [R * C, 1]
        elif self.model.filter_type == "inductive":
            # RL low-pass filter
            num = [1]
            den = [L / R, 1]
        else:  # active
            # First-order active low-pass filter
            tau = 1 / (2 * np.pi * cutoff)
            num = [opamp_gain]
            den = [tau, 1]
            # Include regulator effect if active
            if self.model.regulator_type == "linear":
                vref = max(self.model.linear_vref, 1e-3)
                num = [opamp_gain * vref]
            elif self.model.regulator_type == "switching":
                # Simplified buck converter model (average)
                input_v = max(self.model.input_voltage * self.model.turns_ratio * np.sqrt(2), 1e-3)
                duty_cycle = min(self.model.linear_vref / input_v, 1)
                num = [opamp_gain * duty_cycle]
        # Ensure non-zero coefficients
        num = [max(n, 1e-6) for n in num]
        den = [max(d, 1e-6) for d in den]
        return signal.TransferFunction(num, den)

    def update_plots(self):
        """Update Bode, Nyquist, and root locus plots."""
        if not self.model.power_on:
            self.bode_plot.clear()
            self.phase_plot.clear()
            self.nyquist_plot.clear()
            self.root_locus_plot.clear()
            return

        system = self.get_system()
        w = np.logspace(0, 5, 1000)  # Frequency range: 1 Hz to 100 kHz

        # Bode Plot
        w, mag, phase = signal.bode(system, w)
        self.bode_plot.clear()
        self.bode_plot.plot(w, mag, pen=pg.mkPen(color="#FFFF99", width=2))
        self.phase_plot.clear()
        self.phase_plot.plot(w, phase, pen=pg.mkPen(color="#FFFF99", width=2))

        # Nyquist Plot
        w, H = signal.freqresp(system, w)
        real, imag = H.real, H.imag
        self.nyquist_plot.clear()
        self.nyquist_plot.plot(real, imag, pen=pg.mkPen(color="#FFFF99", width=2))
        # Add -1 point
        self.nyquist_plot.plot([-1], [0], symbol="o", symbolPen="#FF0000", symbolBrush="#FF0000")

        # Root Locus
        self.root_locus_plot.clear()
        try:
            # Convert scipy.signal.TransferFunction to control.TransferFunction
            control_system = ControlTF(system.num, system.den)
            rl_map = control.root_locus_map(control_system, gains=np.linspace(0, 100, 1000))
            r = rl_map.poles
            # Handle different pole data shapes
            if len(r.shape) == 1:
                # Single set of poles (1D array)
                self.root_locus_plot.plot(r.real, r.imag, pen=None, symbol="o", 
                                        symbolPen="#FFFF99", symbolBrush="#FFFF99", symbolSize=5)
            else:
                # Multiple sets of poles (2D array)
                for i in range(r.shape[1]):
                    self.root_locus_plot.plot(r[:, i].real, r[:, i].imag, pen=None, symbol="o", 
                                            symbolPen="#FFFF99", symbolBrush="#FFFF99", symbolSize=5)
        except Exception as e:
            print(f"Root locus calculation failed: {e}")
            # Clear plot to avoid displaying invalid data
            self.root_locus_plot.clear()

    def get_widget(self):
        """Return the widget containing stability plots."""
        return self.widget
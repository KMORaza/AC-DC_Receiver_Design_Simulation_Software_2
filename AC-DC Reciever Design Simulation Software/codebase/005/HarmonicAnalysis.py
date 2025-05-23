import numpy as np
from scipy import fft
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QCheckBox, QPushButton, QGroupBox, QToolTip
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import csv
import os

class HarmonicAnalyzer:
    def __init__(self, model):
        self.model = model
        self.max_harmonics = 10  # Default number of harmonics
        self.log_scale = False  # Default to linear scale
        self.init_ui()

    def init_ui(self):
        """Initialize plot widget for harmonic distortion analysis."""
        self.widget = QWidget()
        layout = QVBoxLayout()

        # THD Label
        self.thd_label = QLabel("THD+N: 0.00%")
        self.thd_label.setObjectName("led-label")
        layout.addWidget(self.thd_label)

        # Harmonic Range Slider
        harmonic_range_group = QGroupBox("HARMONIC RANGE")
        harmonic_range_group.setObjectName("panel")
        range_layout = QHBoxLayout()
        range_label = QLabel("Max Harmonics:")
        range_label.setObjectName("led-label")
        self.harmonic_slider = QSlider(Qt.Horizontal)
        self.harmonic_slider.setRange(5, 20)
        self.harmonic_slider.setValue(self.max_harmonics)
        self.harmonic_slider.valueChanged.connect(self.update_harmonic_range)
        self.harmonic_value = QLabel(str(self.max_harmonics))
        self.harmonic_value.setObjectName("led-display")
        range_layout.addWidget(range_label)
        range_layout.addWidget(self.harmonic_slider)
        range_layout.addWidget(self.harmonic_value)
        harmonic_range_group.setLayout(range_layout)
        layout.addWidget(harmonic_range_group)

        # Log Scale Checkbox
        self.log_checkbox = QCheckBox("Logarithmic Scale")
        self.log_checkbox.setStyleSheet("""
            QCheckBox {
                color: #FFFF99;
                font: 12pt 'Courier New';
            }
        """)
        self.log_checkbox.stateChanged.connect(self.toggle_log_scale)
        layout.addWidget(self.log_checkbox)

        # Harmonic Spectrum Plot
        self.spectrum_label = QLabel("HARMONIC SPECTRUM")
        self.spectrum_label.setObjectName("led-label")
        layout.addWidget(self.spectrum_label)
        self.spectrum_plot = pg.PlotWidget()
        self.spectrum_plot.setBackground("#0A0A0A")
        self.spectrum_plot.setTitle("Harmonic Spectrum", color="#FFFF99", size="12pt")
        self.spectrum_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.spectrum_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.spectrum_plot.showGrid(x=True, y=True, alpha=0.3)
        self.spectrum_plot.setLabel("left", "Amplitude (V)", color="#FFFF99")
        self.spectrum_plot.setLabel("bottom", "Harmonic Number", color="#FFFF99")
        self.spectrum_plot.setMouseEnabled(x=False, y=True)
        self.spectrum_plot.scene().sigMouseMoved.connect(self.show_harmonic_info)
        layout.addWidget(self.spectrum_plot)

        # Export Button
        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_data)
        self.export_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #5C5C5C, stop:1 #3A3A3A);
                border: 3px outset #6C6C6C;
                border-radius: 5px;
                padding: 6px;
                color: #FFFFFF;
                font: bold 12pt 'Courier New';
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #6C6C6C, stop:1 #4A4A4A);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3A3A3A, stop:1 #2E2E2E);
                border: 3px inset #6C6C6C;
            }
        """)
        layout.addWidget(self.export_button)

        self.widget.setLayout(layout)

    def update_harmonic_range(self, value):
        """Update the number of harmonics to analyze."""
        self.max_harmonics = value
        self.harmonic_value.setText(str(value))
        self.update_plots()

    def toggle_log_scale(self, state):
        """Toggle logarithmic scale for the spectrum plot."""
        self.log_scale = state == Qt.Checked
        self.spectrum_plot.setLogMode(y=self.log_scale)
        self.update_plots()

    def show_harmonic_info(self, pos):
        """Show harmonic power contribution on mouse hover."""
        if not hasattr(self, 'last_harmonic_indices'):
            return
        mouse_point = self.spectrum_plot.getViewBox().mapSceneToView(pos)
        x = mouse_point.x()
        if x < 1 or x > self.max_harmonics:
            QToolTip.hideText()
            return
        harmonic = int(round(x))
        if harmonic in self.last_harmonic_indices:
            idx = self.last_harmonic_indices.index(harmonic)
            amp = self.last_harmonic_amps[idx]
            power = amp ** 2
            total_harmonic_power = sum(a ** 2 for a in self.last_harmonic_amps[1:])
            contribution = (power / total_harmonic_power * 100) if total_harmonic_power > 0 else 0
            QToolTip.showText(pos.toPoint(), f"Harmonic {harmonic}: {amp:.4f} V\nPower Contribution: {contribution:.2f}%")

    def update_plots(self):
        """Update THD+N and harmonic spectrum plot."""
        if not self.model.power_on:
            self.thd_label.setText("THD+N: 0.00%")
            self.spectrum_plot.clear()
            self.last_harmonic_indices = []
            self.last_harmonic_amps = []
            return

        # Get modulated signal
        t = np.linspace(0, 0.1, 1000)  # Match Main.py time range
        _, _, modulated = self.model.generate_waveform(t)
        
        # Compute FFT
        N = len(modulated)
        fft_vals = fft.fft(modulated)
        freqs = fft.fftfreq(N, t[1] - t[0])
        fft_vals = fft_vals[:N//2]
        freqs = freqs[:N//2]
        amplitudes = np.abs(fft_vals) / N

        # Find fundamental frequency
        fundamental_freq = self.model.frequency
        fundamental_idx = np.argmin(np.abs(freqs - fundamental_freq))
        fundamental_amp = amplitudes[fundamental_idx] if fundamental_idx < len(amplitudes) else 0

        # Compute harmonics
        harmonic_indices = []
        harmonic_amps = []
        for n in range(1, self.max_harmonics + 1):
            harmonic_freq = fundamental_freq * n
            idx = np.argmin(np.abs(freqs - harmonic_freq))
            if idx < len(amplitudes):
                harmonic_indices.append(n)
                harmonic_amps.append(amplitudes[idx])

        # Estimate noise (non-harmonic components)
        harmonic_mask = np.zeros(len(amplitudes), dtype=bool)
        for n in range(1, self.max_harmonics + 1):
            idx = np.argmin(np.abs(freqs - fundamental_freq * n))
            if idx < len(amplitudes):
                harmonic_mask[idx] = True
        noise_amps = amplitudes[~harmonic_mask]
        noise_power = np.sum(noise_amps ** 2)

        # Calculate THD+N
        if fundamental_amp > 1e-6:
            harmonic_power = sum(amp ** 2 for amp in harmonic_amps[1:])  # Exclude fundamental
            total_distortion_power = harmonic_power + noise_power
            thd_n = 100 * np.sqrt(total_distortion_power) / fundamental_amp
        else:
            thd_n = 0.0
        self.thd_label.setText(f"THD+N: {thd_n:.2f}%")

        # Plot harmonic spectrum
        self.spectrum_plot.clear()
        bar = pg.BarGraphItem(x=harmonic_indices, height=harmonic_amps, width=0.4, brush="#FFFF99")
        self.spectrum_plot.addItem(bar)
        self.spectrum_plot.getAxis("bottom").setTicks([[(i, str(i)) for i in harmonic_indices]])
        self.spectrum_plot.setLogMode(y=self.log_scale)

        # Store for tooltip
        self.last_harmonic_indices = harmonic_indices
        self.last_harmonic_amps = harmonic_amps

    def export_data(self):
        """Export THD+N and harmonic data to CSV."""
        if not hasattr(self, 'last_harmonic_indices'):
            return
        filename = f"harmonic_data_{int(self.model.frequency)}Hz.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["THD+N (%)", self.thd_label.text().split(': ')[1]])
            writer.writerow(["Harmonic", "Amplitude (V)", "Power Contribution (%)"])
            total_harmonic_power = sum(a ** 2 for a in self.last_harmonic_amps[1:]) if len(self.last_harmonic_amps) > 1 else 1e-6
            for n, amp in zip(self.last_harmonic_indices, self.last_harmonic_amps):
                power = amp ** 2
                contribution = (power / total_harmonic_power * 100) if total_harmonic_power > 0 else 0
                writer.writerow([n, f"{amp:.4f}", f"{contribution:.2f}"])
        print(f"Exported harmonic data to {filename}")

    def get_widget(self):
        """Return the widget containing harmonic analysis plots."""
        return self.widget
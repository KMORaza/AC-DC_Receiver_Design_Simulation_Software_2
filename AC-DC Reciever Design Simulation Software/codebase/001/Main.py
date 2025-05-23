import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QComboBox, QPushButton, QSlider, QSplitter, QApplication,
    QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QDoubleValidator, QFont
from ReceiverModel import ReceiverModel

class ControlPanel(QWidget):
    def __init__(self, model, update_callback):
        super().__init__()
        self.model = model
        self.update_callback = update_callback
        self.init_ui()

    def init_ui(self):
        # Create a widget and layout for the scrollable content
        content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Frequency control
        freq_group = QGroupBox("FREQUENCY (Hz)")
        freq_group.setObjectName("panel")
        freq_layout = QHBoxLayout()
        freq_label = QLabel("FREQ:")
        freq_label.setObjectName("led-label")
        self.freq_value = QLabel("1000")
        self.freq_value.setObjectName("led-display")
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(100, 10000)
        self.freq_slider.setValue(1000)
        self.freq_slider.setMinimumWidth(300)
        self.freq_slider.valueChanged.connect(self.update_frequency)
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_slider)
        freq_layout.addWidget(self.freq_value)
        freq_group.setLayout(freq_layout)
        layout.addWidget(freq_group)

        # Gain control
        gain_group = QGroupBox("GAIN (dB)")
        gain_group.setObjectName("panel")
        gain_layout = QHBoxLayout()
        gain_label = QLabel("GAIN:")
        gain_label.setObjectName("led-label")
        self.gain_value = QLabel("0")
        self.gain_value.setObjectName("led-display")
        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setRange(-20, 20)
        self.gain_slider.setValue(0)
        self.gain_slider.setMinimumWidth(300)
        self.gain_slider.valueChanged.connect(self.update_gain)
        gain_layout.addWidget(gain_label)
        gain_layout.addWidget(self.gain_slider)
        gain_layout.addWidget(self.gain_value)
        gain_group.setLayout(gain_layout)
        layout.addWidget(gain_group)

        # Signal mode control
        signal_group = QGroupBox("SIGNAL MODE")
        signal_group.setObjectName("panel")
        signal_layout = QHBoxLayout()
        self.signal_combo = QComboBox()
        self.signal_combo.addItems(["Analog", "Digital", "Mixed"])
        self.signal_combo.currentTextChanged.connect(self.update_signal_mode)
        signal_layout.addWidget(self.signal_combo)
        signal_group.setLayout(signal_layout)
        layout.addWidget(signal_group)

        # Modulation control
        mod_group = QGroupBox("MODULATION")
        mod_group.setObjectName("panel")
        mod_layout = QHBoxLayout()
        self.mod_button_am = QPushButton("AM")
        self.mod_button_am.setCheckable(True)
        self.mod_button_am.clicked.connect(lambda: self.update_modulation("AM"))
        self.mod_button_fm = QPushButton("FM")
        self.mod_button_fm.setCheckable(True)
        self.mod_button_fm.clicked.connect(lambda: self.update_modulation("FM"))
        mod_layout.addWidget(self.mod_button_am)
        mod_layout.addWidget(self.mod_button_fm)
        mod_layout.addStretch()
        mod_group.setLayout(mod_layout)
        layout.addWidget(mod_group)

        # Analysis mode control
        analysis_group = QGroupBox("ANALYSIS MODE")
        analysis_group.setObjectName("panel")
        analysis_layout = QHBoxLayout()
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems(["Transient", "Steady-State", "Frequency"])
        self.analysis_combo.currentTextChanged.connect(self.update_analysis_mode)
        analysis_layout.addWidget(self.analysis_combo)
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)

        # Rectifier control
        rect_group = QGroupBox("RECTIFIER")
        rect_group.setObjectName("panel")
        rect_layout = QHBoxLayout()
        self.rect_combo = QComboBox()
        self.rect_combo.addItems(["Half-Wave", "Full-Wave", "Bridge"])
        self.rect_combo.currentTextChanged.connect(self.update_rectifier)
        rect_layout.addWidget(self.rect_combo)
        rect_group.setLayout(rect_layout)
        layout.addWidget(rect_group)

        # Filter control
        filter_group = QGroupBox("FILTER TYPE")
        filter_group.setObjectName("panel")
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Capacitive", "Inductive", "Active"])
        self.filter_combo.currentTextChanged.connect(self.update_filter_type)
        filter_layout.addWidget(self.filter_combo)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Filter parameters
        filter_params_group = QGroupBox("FILTER PARAMETERS")
        filter_params_group.setObjectName("panel")
        filter_params_layout = QVBoxLayout()
        self.cap_input = QLineEdit("100")
        self.cap_input.setValidator(QDoubleValidator(0, 1000, 2))
        self.cap_input.textChanged.connect(self.update_capacitance)
        filter_params_layout.addWidget(QLabel("CAP (µF):").setObjectName("led-label"))
        filter_params_layout.addWidget(self.cap_input)
        self.inductance_input = QLineEdit("10")
        self.inductance_input.setValidator(QDoubleValidator(0.1, 100, 2))
        self.inductance_input.textChanged.connect(self.update_inductance)
        filter_params_layout.addWidget(QLabel("IND (mH):").setObjectName("led-label"))
        filter_params_layout.addWidget(self.inductance_input)
        self.active_cutoff_input = QLineEdit("100")
        self.active_cutoff_input.setValidator(QDoubleValidator(10, 1000, 2))
        self.active_cutoff_input.textChanged.connect(self.update_active_cutoff)
        filter_params_layout.addWidget(QLabel("CUTOFF (Hz):").setObjectName("led-label"))
        filter_params_layout.addWidget(self.active_cutoff_input)
        filter_params_group.setLayout(filter_params_layout)
        layout.addWidget(filter_params_group)

        # Regulator control
        reg_group = QGroupBox("REGULATOR")
        reg_group.setObjectName("panel")
        reg_layout = QHBoxLayout()
        self.reg_combo = QComboBox()
        self.reg_combo.addItems(["None", "Linear", "Switching"])
        self.reg_combo.currentTextChanged.connect(self.update_regulator_type)
        reg_layout.addWidget(self.reg_combo)
        reg_group.setLayout(reg_layout)
        layout.addWidget(reg_group)

        # Regulator parameters
        reg_params_group = QGroupBox("REGULATOR PARAMETERS")
        reg_params_group.setObjectName("panel")
        reg_params_layout = QVBoxLayout()
        self.vref_input = QLineEdit("5.0")
        self.vref_input.setValidator(QDoubleValidator(1.0, 20.0, 2))
        self.vref_input.textChanged.connect(self.update_vref)
        reg_params_layout.addWidget(QLabel("VREF (V):").setObjectName("led-label"))
        reg_params_layout.addWidget(self.vref_input)
        self.switching_freq_input = QLineEdit("10000")
        self.switching_freq_input.setValidator(QDoubleValidator(1000, 50000, 2))
        self.switching_freq_input.textChanged.connect(self.update_switching_freq)
        reg_params_layout.addWidget(QLabel("SW FREQ (Hz):").setObjectName("led-label"))
        reg_params_layout.addWidget(self.switching_freq_input)
        reg_params_group.setLayout(reg_params_layout)
        layout.addWidget(reg_params_group)

        # Transformer turns ratio control
        turns_group = QGroupBox("TRANSFORMER")
        turns_group.setObjectName("panel")
        turns_layout = QVBoxLayout()
        self.turns_input = QLineEdit("1.0")
        self.turns_input.setValidator(QDoubleValidator(0.1, 10.0, 2))
        self.turns_input.textChanged.connect(self.update_turns_ratio)
        turns_layout.addWidget(QLabel("TURNS RATIO:").setObjectName("led-label"))
        turns_layout.addWidget(self.turns_input)
        turns_group.setLayout(turns_layout)
        layout.addWidget(turns_group)

        # Coil inductance control
        coil_group = QGroupBox("COIL")
        coil_group.setObjectName("panel")
        coil_layout = QVBoxLayout()
        self.coil_inductance_input = QLineEdit("1.0")
        self.coil_inductance_input.setValidator(QDoubleValidator(0.1, 10.0, 2))
        self.coil_inductance_input.textChanged.connect(self.update_coil_inductance)
        coil_layout.addWidget(QLabel("IND (mH):").setObjectName("led-label"))
        coil_layout.addWidget(self.coil_inductance_input)
        coil_group.setLayout(coil_layout)
        layout.addWidget(coil_group)

        # Nonlinear device parameters
        nonlinear_group = QGroupBox("NONLINEAR DEVICES")
        nonlinear_group.setObjectName("panel")
        nonlinear_layout = QVBoxLayout()
        self.diode_is_input = QLineEdit("1e-12")
        self.diode_is_input.setValidator(QDoubleValidator(1e-15, 1e-9, 15))
        self.diode_is_input.textChanged.connect(self.update_diode_is)
        nonlinear_layout.addWidget(QLabel("DIODE Is (A):").setObjectName("led-label"))
        nonlinear_layout.addWidget(self.diode_is_input)
        self.mosfet_vth_input = QLineEdit("2.0")
        self.mosfet_vth_input.setValidator(QDoubleValidator(0.5, 5.0, 2))
        self.mosfet_vth_input.textChanged.connect(self.update_mosfet_vth)
        nonlinear_layout.addWidget(QLabel("MOSFET Vth (V):").setObjectName("led-label"))
        nonlinear_layout.addWidget(self.mosfet_vth_input)
        nonlinear_group.setLayout(nonlinear_layout)
        layout.addWidget(nonlinear_group)

        # Power toggle
        self.power_button = QPushButton("POWER")
        self.power_button.setCheckable(True)
        self.power_button.clicked.connect(self.toggle_power)
        layout.addWidget(self.power_button)

        # Analysis results
        analysis_group = QGroupBox("ANALYSIS DISPLAY")
        analysis_group.setObjectName("panel")
        analysis_layout = QVBoxLayout()
        self.ripple_label = QLabel("RIPPLE: 0.00 V")
        self.ripple_label.setObjectName("led-display")
        self.avg_voltage_label = QLabel("AVG V: 0.00 V")
        self.avg_voltage_label.setObjectName("led-display")
        self.thd_label = QLabel("THD: 0.00 %")
        self.thd_label.setObjectName("led-display")
        self.phase_label = QLabel("PHASE: 0.00 °")
        self.phase_label.setObjectName("led-display")
        self.power_label = QLabel("POWER: 0.00 W")
        self.power_label.setObjectName("led-display")
        self.temp_label = QLabel("TEMP: 25.00 °C")
        self.temp_label.setObjectName("led-display")
        self.eff_label = QLabel("EFF: 100.00 %")
        self.eff_label.setObjectName("led-display")
        analysis_layout.addWidget(self.ripple_label)
        analysis_layout.addWidget(self.avg_voltage_label)
        analysis_layout.addWidget(self.thd_label)
        analysis_layout.addWidget(self.phase_label)
        analysis_layout.addWidget(self.power_label)
        analysis_layout.addWidget(self.temp_label)
        analysis_layout.addWidget(self.eff_label)
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)

        layout.addStretch()
        content_widget.setLayout(layout)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: #2E2E2E;
                border: none;
            }
            QScrollBar:vertical {
                background: #2E2E2E;
                width: 16px;
                margin: 0px;
                border: 1px solid #5C5C5C;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #6C6C6C, stop:1 #4A4A4A);
                border: 1px solid #5C5C5C;
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: #3A3A3A;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: #2E2E2E;
            }
        """)

        # Set scroll area as the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        # Apply electronic equipment QSS
        content_widget.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2E2E2E;  /* Dark metallic chassis */
                color: #FFFFFF;
                font-family: 'Courier New';
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
            QLineEdit, QComboBox {
                background: #1A1A1A;
                border: 2px inset #5C5C5C;
                border-radius: 3px;
                padding: 4px;
                color: #FFFF99;  /* Light yellow LED-like text */
                font: 12pt 'Courier New';
            }
            QComboBox::drop-down {
                border: 2px outset #5C5C5C;
                background: #3A3A3A;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFFFFF;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #5C5C5C, stop:1 #3A3A3A);
                border: 3px outset #6C6C6C;
                border-radius: 5px;
                padding: 6px;
                color: #FFFFFF;
                font: bold 12pt 'Courier New';
                min-width: 80px;
                min-height: 30px;
            }
            QPushButton:checked, QPushButton:pressed {
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
                color: #FFFF99;  /* Light yellow LED-like display */
                font: 12pt 'Courier New';
            }
        """)

    def update_frequency(self, value):
        try:
            self.model.set_frequency(int(value))
            self.freq_value.setText(str(value))
            self.update_callback()
        except ValueError:
            pass

    def update_gain(self, value):
        try:
            self.model.set_gain(int(value))
            self.gain_value.setText(str(value))
            self.update_callback()
        except ValueError:
            pass

    def update_signal_mode(self, text):
        self.model.set_signal_mode(text.lower())
        self.update_callback()

    def update_modulation(self, mod_type):
        self.model.set_modulation(mod_type)
        self.mod_button_am.setChecked(mod_type == "AM")
        self.mod_button_fm.setChecked(mod_type == "FM")
        self.update_callback()

    def update_analysis_mode(self, text):
        self.model.set_analysis_mode(text.replace("-", "_").lower())
        self.update_callback()

    def update_rectifier(self, text):
        rectifier_map = {"Half-Wave": "half_wave", "Full-Wave": "full_wave", "Bridge": "bridge"}
        self.model.rectifier_type = rectifier_map[text]
        self.update_callback()

    def update_filter_type(self, text):
        self.model.set_filter_type(text.lower())
        self.update_callback()

    def update_capacitance(self):
        try:
            cap = float(self.cap_input.text()) * 1e-6
            self.model.filter_capacitance = cap
            self.update_callback()
        except ValueError:
            pass

    def update_inductance(self):
        try:
            inductance = float(self.inductance_input.text()) * 1e-3
            self.model.set_filter_inductance(inductance)
            self.update_callback()
        except ValueError:
            pass

    def update_active_cutoff(self):
        try:
            cutoff = float(self.active_cutoff_input.text())
            self.model.set_active_filter_cutoff(cutoff)
            self.update_callback()
        except ValueError:
            pass

    def update_regulator_type(self, text):
        self.model.set_regulator_type(text.lower())
        self.update_callback()

    def update_vref(self):
        try:
            vref = float(self.vref_input.text())
            self.model.set_linear_vref(vref)
            self.update_callback()
        except ValueError:
            pass

    def update_switching_freq(self):
        try:
            freq = float(self.switching_freq_input.text())
            self.model.set_switching_freq(freq)
            self.update_callback()
        except ValueError:
            pass

    def update_turns_ratio(self):
        try:
            ratio = float(self.turns_input.text())
            if ratio > 5:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Warning", "High turns ratio may cause numerical instability.")
            self.model.turns_ratio = ratio
            self.update_callback()
        except ValueError:
            pass

    def update_coil_inductance(self):
        try:
            inductance = float(self.coil_inductance_input.text()) * 1e-3
            self.model.set_coil_inductance(inductance)
            self.update_callback()
        except ValueError:
            pass

    def update_diode_is(self):
        try:
            diode_is = float(self.diode_is_input.text())
            self.model.diode_is = diode_is
            self.update_callback()
        except ValueError:
            pass

    def update_mosfet_vth(self):
        try:
            vth = float(self.mosfet_vth_input.text())
            self.model.mosfet_vth = vth
            self.update_callback()
        except ValueError:
            pass

    def toggle_power(self, checked):
        self.model.set_power(checked)
        self.power_button.setText(f"POWER: {'ON' if checked else 'OFF'}")
        self.update_callback()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = ReceiverModel()
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(100)

    def init_ui(self):
        self.setWindowTitle("AC/DC Receiver Simulator")
        self.setGeometry(100, 100, 1600, 1000)

        splitter = QSplitter(Qt.Horizontal)
        self.control_panel = ControlPanel(self.model, self.update_plots)
        splitter.addWidget(self.control_panel)

        plot_container = QWidget()
        plot_layout = QVBoxLayout()

        # AC waveform plot
        self.ac_label = QLabel("AC INPUT")
        self.ac_label.setObjectName("led-label")
        plot_layout.addWidget(self.ac_label)
        self.ac_plot = pg.PlotWidget()
        self.ac_plot.setBackground("#0A0A0A")  # Oscilloscope-like dark background
        self.ac_plot.setTitle("AC Waveform", color="#FFFF99", size="12pt")
        self.ac_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.ac_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.ac_plot.showGrid(x=True, y=True, alpha=0.3)
        plot_layout.addWidget(self.ac_plot)

        # Rectified waveform plot
        self.rect_label = QLabel("RECTIFIED")
        self.rect_label.setObjectName("led-label")
        plot_layout.addWidget(self.rect_label)
        self.rect_plot = pg.PlotWidget()
        self.rect_plot.setBackground("#0A0A0A")
        self.rect_plot.setTitle("Rectified Waveform", color="#FFFF99", size="12pt")
        self.rect_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.rect_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.rect_plot.showGrid(x=True, y=True, alpha=0.3)
        plot_layout.addWidget(self.rect_plot)

        # Modulated waveform plot
        self.waveform_label = QLabel("MODULATED")
        self.waveform_label.setObjectName("led-label")
        plot_layout.addWidget(self.waveform_label)
        self.waveform_plot = pg.PlotWidget()
        self.waveform_plot.setBackground("#0A0A0A")
        self.waveform_plot.setTitle("Waveform", color="#FFFF99", size="12pt")
        self.waveform_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.waveform_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.waveform_plot.showGrid(x=True, y=True, alpha=0.3)
        plot_layout.addWidget(self.waveform_plot)

        # Frequency spectrum
        self.spectrum_label = QLabel("SPECTRUM")
        self.spectrum_label.setObjectName("led-label")
        plot_layout.addWidget(self.spectrum_label)
        self.spectrum_plot = pg.PlotWidget()
        self.spectrum_plot.setBackground("#0A0A0A")
        self.spectrum_plot.setTitle("Spectrum", color="#FFFF99", size="12pt")
        self.spectrum_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.spectrum_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.spectrum_plot.showGrid(x=True, y=True, alpha=0.3)
        plot_layout.addWidget(self.spectrum_plot)

        plot_container.setLayout(plot_layout)
        splitter.addWidget(plot_container)
        splitter.setSizes([600, 1000])

        self.setCentralWidget(splitter)

        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4A4A4A, stop:1 #2E2E2E);
            }
            QLabel#led-label {
                background: transparent;
                color: #FFFFFF;
                font: bold 12pt 'Courier New';
            }
        """)

    def update_plots(self):
        if not self.model.power_on:
            self.ac_plot.clear()
            self.rect_plot.clear()
            self.waveform_plot.clear()
            self.spectrum_plot.clear()
            self.control_panel.ripple_label.setText("RIPPLE: 0.00 V")
            self.control_panel.avg_voltage_label.setText("AVG V: 0.00 V")
            self.control_panel.thd_label.setText("THD: 0.00 %")
            self.control_panel.phase_label.setText("PHASE: 0.00 °")
            self.control_panel.power_label.setText("POWER: 0.00 W")
            self.control_panel.temp_label.setText("TEMP: 25.00 °C")
            self.control_panel.eff_label.setText("EFF: 100.00 %")
            return

        t = np.linspace(0, 0.1, 1000)
        ac_signal, rectified_signal, modulated_signal = self.model.generate_waveform(t)
        analysis = self.model.analyze_waveform(modulated_signal, t)

        # Update AC plot
        self.ac_plot.clear()
        self.ac_plot.plot(t, ac_signal, pen=pg.mkPen(color="#FFFF99", width=2))

        # Update rectified plot
        self.rect_plot.clear()
        self.rect_plot.plot(t, rectified_signal, pen=pg.mkPen(color="#FFFF99", width=2))

        # Update waveform plot
        self.waveform_plot.clear()
        self.waveform_plot.plot(t, modulated_signal, pen=pg.mkPen(color="#FFFF99", width=2))

        # Update spectrum plot
        fft = np.abs(np.fft.fft(modulated_signal))[:len(modulated_signal)//2]
        freqs = np.fft.fftfreq(len(modulated_signal), 0.1/1000)[:len(modulated_signal)//2]
        self.spectrum_plot.clear()
        self.spectrum_plot.plot(freqs, fft, pen=pg.mkPen(color="#FFFF99", width=2))

        # Update analysis results
        self.control_panel.ripple_label.setText(f"RIPPLE: {analysis.get('ripple_voltage', 0):.2f} V")
        self.control_panel.avg_voltage_label.setText(f"AVG V: {analysis.get('avg_voltage', 0):.2f} V")
        self.control_panel.thd_label.setText(f"THD: {analysis.get('thd', 0):.2f} %")
        self.control_panel.phase_label.setText(f"PHASE: {analysis.get('phase', 0):.2f} °")
        self.control_panel.power_label.setText(f"POWER: {analysis.get('power', 0):.2f} W")
        self.control_panel.temp_label.setText(f"TEMP: {self.model.temperature:.2f} °C")
        self.control_panel.eff_label.setText(f"EFF: {self.model.efficiency*100:.2f} %")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
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
from StabilityAnalysis import StabilityAnalyzer
from HarmonicAnalysis import HarmonicAnalyzer
from PowerFactorCorrection import PowerFactorCorrection
from SNR_Analysis import SNRAnalyzer
from THD_Analysis import THDAnalyzer
from EMI_Analysis import EMIAnalyzer
import time

class ControlPanel(QWidget):
    def __init__(self, model, update_callback):
        super().__init__()
        self.model = model
        self.update_callback = update_callback
        self.dynamic_mode = False
        self.noise_level = 0.0
        self.dynamic_start_time = None
        self.init_ui()

    def init_ui(self):
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
        nonlinear_layout.setAlignment(Qt.AlignTop)
        nonlinear_group.setLayout(nonlinear_layout)
        layout.addWidget(nonlinear_group)

        # Power factor correction control
        pfc_group = QGroupBox("POWER FACTOR CORRECTION")
        pfc_group.setObjectName("panel")
        pfc_layout = QHBoxLayout()
        self.pfc_button = QPushButton("PFC: OFF")
        self.pfc_button.setCheckable(True)
        self.pfc_button.clicked.connect(self.toggle_pfc)
        self.pfc_combo = QComboBox()
        self.pfc_combo.addItems(["None", "Active Boost", "Passive"])
        self.pfc_combo.currentTextChanged.connect(self.update_pfc_type)
        pfc_layout.addWidget(self.pfc_button)
        pfc_layout.addWidget(self.pfc_combo)
        pfc_group.setLayout(pfc_layout)
        layout.addWidget(pfc_group)

        # Dynamic mode toggle
        dynamic_group = QGroupBox("DYNAMIC SIMULATION")
        dynamic_group.setObjectName("panel")
        dynamic_layout = QHBoxLayout()
        self.dynamic_button = QPushButton("DYNAMIC: OFF")
        self.dynamic_button.setCheckable(True)
        self.dynamic_button.clicked.connect(self.toggle_dynamic_mode)
        dynamic_layout.addWidget(self.dynamic_button)
        dynamic_group.setLayout(dynamic_layout)
        layout.addWidget(dynamic_group)

        # Noise level control
        noise_group = QGroupBox("NOISE LEVEL")
        noise_group.setObjectName("panel")
        noise_layout = QHBoxLayout()
        noise_label = QLabel("NOISE:")
        noise_label.setObjectName("led-label")
        self.noise_slider = QSlider(Qt.Horizontal)
        self.noise_slider.setRange(0, 100)
        self.noise_slider.setValue(0)
        self.noise_slider.setMinimumWidth(300)
        self.noise_slider.valueChanged.connect(self.update_noise_level)
        self.noise_value = QLabel("0.00")
        self.noise_value.setObjectName("led-display")
        noise_layout.addWidget(noise_label)
        noise_layout.addWidget(self.noise_slider)
        noise_layout.addWidget(self.noise_value)
        noise_group.setLayout(noise_layout)
        layout.addWidget(noise_group)

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
        self.thdp_label = QLabel("THD-P: 0.00 %")
        self.thdp_label.setObjectName("led-display")
        self.snr_label = QLabel("SNR: 0.00 dB")
        self.snr_label.setObjectName("led-display")
        self.emi_label = QLabel("EMI: 0.00 dBµV")
        self.emi_label.setObjectName("led-display")
        self.phase_label = QLabel("PHASE: 0.00 °")
        self.phase_label.setObjectName("led-display")
        self.power_label = QLabel("POWER: 0.00 W")
        self.power_label.setObjectName("led-display")
        self.temp_label = QLabel("TEMP: 25.00 °C")
        self.temp_label.setObjectName("led-display")
        self.eff_label = QLabel("EFF: 100.00 %")
        self.eff_label.setObjectName("led-display")
        self.pf_label = QLabel("PF: 1.00")
        self.pf_label.setObjectName("led-display")
        analysis_layout.addWidget(self.ripple_label)
        analysis_layout.addWidget(self.avg_voltage_label)
        analysis_layout.addWidget(self.thd_label)
        analysis_layout.addWidget(self.thdp_label)
        analysis_layout.addWidget(self.snr_label)
        analysis_layout.addWidget(self.emi_label)
        analysis_layout.addWidget(self.phase_label)
        analysis_layout.addWidget(self.power_label)
        analysis_layout.addWidget(self.temp_label)
        analysis_layout.addWidget(self.eff_label)
        analysis_layout.addWidget(self.pf_label)
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)

        layout.addStretch()
        content_widget.setLayout(layout)

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

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        content_widget.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2E2E2E;
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
                color: #FFFF99;
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
                color: #FFFF99;
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
        if not checked:
            self.dynamic_start_time = None
        self.update_callback()

    def toggle_dynamic_mode(self, checked):
        self.dynamic_mode = checked
        self.dynamic_button.setText(f"DYNAMIC: {'ON' if checked else 'OFF'}")
        if checked and self.model.power_on:
            self.dynamic_start_time = time.time()
        else:
            self.dynamic_start_time = None
        self.update_callback()

    def update_noise_level(self, value):
        self.noise_level = value / 100.0
        self.noise_value.setText(f"{self.noise_level:.2f}")
        self.update_callback()

    def toggle_pfc(self, checked):
        self.pfc_enabled = checked
        self.pfc_button.setText(f"PFC: {'ON' if checked else 'OFF'}")
        pfc_type = self.pfc_combo.currentText().replace(" ", "_").lower()
        self.pfc.set_pfc(checked, pfc_type)
        self.update_callback()

    def update_pfc_type(self, text):
        pfc_type = text.replace(" ", "_").lower()
        self.pfc.set_pfc(self.pfc_enabled, pfc_type)
        self.update_callback()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = ReceiverModel()
        self.stability_analyzer = StabilityAnalyzer(self.model)
        self.harmonic_analyzer = HarmonicAnalyzer(self.model)
        self.pfc = PowerFactorCorrection(self.model)
        self.snr_analyzer = SNRAnalyzer(self.model)
        self.thd_analyzer = THDAnalyzer(self.model)
        self.emi_analyzer = EMIAnalyzer(self.model)
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(50)

    def init_ui(self):
        self.setWindowTitle("AC/DC Receiver Simulator")
        self.setGeometry(100, 100, 1600, 1000)

        splitter = QSplitter(Qt.Horizontal)
        self.control_panel = ControlPanel(self.model, self.update_plots)
        self.control_panel.pfc = self.pfc
        self.control_panel.pfc_enabled = False
        splitter.addWidget(self.control_panel)

        plot_container = QWidget()
        plot_layout = QVBoxLayout()

        self.ac_label = QLabel("AC INPUT")
        self.ac_label.setObjectName("led-label")
        plot_layout.addWidget(self.ac_label)
        self.ac_plot = pg.PlotWidget()
        self.ac_plot.setBackground("#0A0A0A")
        self.ac_plot.setTitle("AC Waveform", color="#FFFF99", size="12pt")
        self.ac_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.ac_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.ac_plot.showGrid(x=True, y=True, alpha=0.3)
        plot_layout.addWidget(self.ac_plot)

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

        analysis_container = QWidget()
        analysis_layout = QVBoxLayout()
        analysis_layout.addWidget(self.stability_analyzer.get_widget())
        analysis_layout.addWidget(self.harmonic_analyzer.get_widget())
        analysis_container.setLayout(analysis_layout)
        splitter.addWidget(analysis_container)

        splitter.setSizes([400, 600, 600])

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
            self.stability_analyzer.update_plots()
            self.harmonic_analyzer.update_plots()
            self.control_panel.ripple_label.setText("RIPPLE: 0.00 V")
            self.control_panel.avg_voltage_label.setText("AVG V: 0.00 V")
            self.control_panel.thd_label.setText("THD: 0.00 %")
            self.control_panel.thdp_label.setText("THD-P: 0.00 %")
            self.control_panel.snr_label.setText("SNR: 0.00 dB")
            self.control_panel.emi_label.setText("EMI: 0.00 dBµV")
            self.control_panel.phase_label.setText("PHASE: 0.00 °")
            self.control_panel.power_label.setText("POWER: 0.00 W")
            self.control_panel.temp_label.setText("TEMP: 25.00 °C")
            self.control_panel.eff_label.setText("EFF: 100.00 %")
            self.control_panel.pf_label.setText("PF: 1.00")
            return

        # Apply dynamic parameters
        if self.control_panel.dynamic_mode and self.control_panel.dynamic_start_time is not None:
            elapsed_time = time.time() - self.control_panel.dynamic_start_time
            base_freq = int(self.control_panel.freq_value.text())
            freq_variation = 0.1 * base_freq * np.sin(0.1 * elapsed_time)
            dynamic_freq = max(100, min(10000, base_freq + freq_variation))
            self.model.set_frequency(int(dynamic_freq))
            self.control_panel.freq_value.setText(f"{int(dynamic_freq)}")

            base_gain = int(self.control_panel.gain_value.text())
            gain_variation = 5 * np.sin(0.05 * elapsed_time)
            dynamic_gain = max(-20, min(20, base_gain + gain_variation))
            self.model.set_gain(int(dynamic_gain))
            self.control_panel.gain_value.setText(f"{int(dynamic_gain)}")

        # Generate waveform data
        t = np.linspace(0, 0.1, 1000)
        fs = 1000 / 0.1  # Sampling frequency (10 kHz)
        ac_signal, rectified_signal, modulated_signal = self.model.generate_waveform(t)

        # Simulate input current
        input_current = np.sin(2 * np.pi * self.model.frequency * t - np.pi / 6) * np.max(np.abs(ac_signal)) / 10

        # Apply PFC
        corrected_current = self.pfc.apply_pfc(t, ac_signal, input_current)
        if self.pfc.pfc_enabled:
            modulation_factor = np.abs(corrected_current) / (np.max(np.abs(input_current)) + 1e-6)
            modulated_signal *= modulation_factor

        # Store clean signal for THD-P calculation
        clean_signal = modulated_signal.copy()

        # Add environmental noise
        if self.control_panel.noise_level > 0:
            noise = np.random.normal(0, self.control_panel.noise_level * np.std(modulated_signal), len(modulated_signal))
            modulated_signal += noise

        # Update analyzers
        self.harmonic_analyzer.update_plots()
        self.snr_analyzer.update(clean_signal, self.control_panel.noise_level)
        self.thd_analyzer.update(clean_signal, fs)
        self.emi_analyzer.update(t, modulated_signal)

        # Analyze waveform for metrics
        analysis = self.model.analyze_waveform(modulated_signal, t)

        # Update waveform plots
        self.ac_plot.clear()
        self.ac_plot.plot(t, ac_signal, pen=pg.mkPen(color="#FFFF99", width=2))
        self.ac_plot.plot(t, corrected_current * 10, pen=pg.mkPen(color="#FF5555", width=1))

        self.rect_plot.clear()
        self.rect_plot.plot(t, rectified_signal, pen=pg.mkPen(color="#FFFF99", width=2))

        self.waveform_plot.clear()
        self.waveform_plot.plot(t, modulated_signal, pen=pg.mkPen(color="#FFFF99", width=2))

        self.spectrum_plot.clear()
        fft = np.abs(np.fft.fft(modulated_signal))[:len(modulated_signal)//2]
        freqs = np.fft.fftfreq(len(modulated_signal), 0.1/1000)[:len(modulated_signal)//2]
        self.spectrum_plot.plot(freqs, fft, pen=pg.mkPen(color="#FFFF99", width=2))

        # Update stability plots
        self.stability_analyzer.update_plots()

        # Update analysis display
        try:
            ripple = analysis.get('ripple_voltage', 0)
            avg_voltage = analysis.get('avg_voltage', 0)
            phase = analysis.get('phase', 0)
            power = analysis.get('power', 0)
            thd_n = float(self.harmonic_analyzer.thd_label.text().split(': ')[1].strip('%'))
            thd_p = self.thd_analyzer.get_thd()
            snr = self.snr_analyzer.get_snr()
            emi = self.emi_analyzer.get_emi_level()
            temperature = self.model.temperature
            efficiency = self.pfc.adjust_efficiency(self.model.efficiency) * 100
            power_factor = self.pfc.get_power_factor()
        except (ValueError, AttributeError, IndexError):
            ripple = avg_voltage = phase = power = thd_n = thd_p = snr = emi = 0.0
            temperature = 25.00
            efficiency = 100.00
            power_factor = 1.00

        self.control_panel.ripple_label.setText(f"RIPPLE: {ripple:.2f} V")
        self.control_panel.avg_voltage_label.setText(f"AVG V: {avg_voltage:.2f} V")
        self.control_panel.thd_label.setText(f"THD: {thd_n:.2f} %")
        self.control_panel.thdp_label.setText(f"THD-P: {thd_p:.2f} %")
        self.control_panel.snr_label.setText(f"SNR: {snr:.2f} dB")
        self.control_panel.emi_label.setText(f"EMI: {emi:.2f} dBµV")
        self.control_panel.phase_label.setText(f"PHASE: {phase:.2f} °")
        self.control_panel.power_label.setText(f"POWER: {power:.2f} W")
        self.control_panel.temp_label.setText(f"TEMP: {temperature:.2f} °C")
        self.control_panel.eff_label.setText(f"EFF: {efficiency:.2f} %")
        self.control_panel.pf_label.setText(f"PF: {power_factor:.2f}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())